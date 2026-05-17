import os
import yaml
import pymongo
import numpy as np
import pandas as pd
from datetime import datetime

# Import the fixed university helper function
from utils import df_rebase

# Map activity IDs to human-readable labels as specified by the PAMAP2 guidelines
ACTIVITY_MAP = {
    1: "lying", 2: "sitting", 3: "standing", 4: "walking", 5: "running",
    6: "cycling", 7: "Nordic walking", 9: "watching TV", 10: "computer work",
    11: "house climbing", 12: "ascending stairs", 13: "descending stairs",
    16: "vacuum cleaning", 17: "ironing", 18: "folding laundry",
    19: "house cleaning", 20: "playing soccer", 24: "rope jumping"
}

# Define column indexes for your professor's df_rebase renaming tool
# Target columns must match the exact length of your reference names list
TARGET_COLS = [4, 5, 6, 10, 11, 12, 1] 
REF_COLS = ["acc_x", "acc_y", "acc_z", "gyr_x", "gyr_y", "gyr_z", "activity_id"]

def load_config():
    with open("config.yml", "r", encoding="utf-8") as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def process_file_with_rebase(file_path, subject, split_name):
    """
    Reads a raw .dat file, maps columns with df_rebase, segments contiguous blocks,
    and returns a list of formatted documents matching the course requirements.
    """
    print(f"Processing Subject {subject} ({split_name})...")
    
    # 1. Load the raw space-separated text data matrix
    raw_df = pd.read_csv(file_path, sep=r"\s+", header=None)
    
    # 2. Reorder and rename columns using the course's rebase utility
    processed_df = df_rebase(raw_df, target_list=TARGET_COLS, ref_list=REF_COLS)
    
    if processed_df is None or processed_df.empty:
        return []

    # 3. Find where the activity changes to segment contiguous execution blocks
    activity_ids = processed_df["activity_id"].values
    activity_changes = np.where(activity_ids[:-1] != activity_ids[1:])[0] + 1
    split_indices = np.concatenate(([0], activity_changes, [len(processed_df)]))
    
    documents = []
    
    for i in range(len(split_indices) - 1):
        start_idx = split_indices[i]
        end_idx = split_indices[i+1]
        
        segment = processed_df.iloc[start_idx:end_idx]
        current_activity = int(segment.iloc[0]["activity_id"])
        
        # Rule: Skip transient states (activity_id == 0)
        if current_activity == 0:
            continue
            
        activity_label = ACTIVITY_MAP.get(current_activity, "unknown")
        
        # Extract individual signal arrays, removing any NaN values cleanly
        acc_x = segment["acc_x"].dropna().tolist()
        acc_y = segment["acc_y"].dropna().tolist()
        acc_z = segment["acc_z"].dropna().tolist()
        
        gyr_x = segment["gyr_x"].dropna().tolist()
        gyr_y = segment["gyr_y"].dropna().tolist()
        gyr_z = segment["gyr_z"].dropna().tolist()
        
        # Skip empty sequences
        if not acc_x or not gyr_x:
            continue
            
        # Structure the target schema matching the assignment expectations
        schema_doc = {
            "data": {
                "acc_x": acc_x,
                "acc_y": acc_y,
                "acc_z": acc_z,
                "gyr_x": gyr_x,
                "gyr_y": gyr_y,
                "gyr_z": gyr_z
            },
            "activity_id": current_activity,
            "activity_label": activity_label,
            "subject": str(subject),
            "split": split_name,
            "imu_location": "hand",
            "sensor": "AccGyr",
            "sr": 100,
            "datetime": datetime.now()
        }
        documents.append(schema_doc)
        
    return documents

def main():
    config = load_config()
    
    # Establish database engine wire protocol
    client = pymongo.MongoClient(config["client"])
    db = client[config["db"]]
    collection = db[config["col"]]
    
    base_data_path = config["data_path"]
    
    print(f"Initializing PAMAP2 Ingestion Pipeline...")
    
    splits = ["Protocol", "Optional"]
    for split in splits:
        split_dir_path = os.path.join(base_data_path, split)
        
        if not os.path.exists(split_dir_path):
            continue
            
        files = sorted([f for f in os.listdir(split_dir_path) if f.endswith(".dat")])
        for file_name in files:
            full_file_path = os.path.join(split_dir_path, file_name)
            subject_key = file_name.replace("subject", "").replace(".dat", "")
            
            # Extract data records using the updated pipeline layout
            docs_batch = process_file_with_rebase(full_file_path, subject_key, split)
            
            if docs_batch:
                print(f"Uploading {len(docs_batch)} structured activity segment documents...")
                collection.insert_many(docs_batch, ordered=False)
                print(f"Synced and saved file: {file_name}\n")

    print(" Success! All eligible data has been processed and uploaded to MongoDB.")

if __name__ == "__main__":
    main()