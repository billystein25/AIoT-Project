import os
import yaml
import pymongo


from data_parser import get_subject_data, transform_subject_to_docs

def load_config():
    with open("config.yml", "r", encoding="utf-8") as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def main():
    config = load_config()
    
    client = pymongo.MongoClient(config["client"])
    db = client[config["db"]]
    collection = db[config["col"]]
    
    base_data_path = config["data_path"]
    print(f"Starting Parsing with data_parser.py...")
    
  
    splits = ["Protocol"]
    for split in splits:
        split_dir_path = os.path.join(base_data_path, split)
        
        if not os.path.exists(split_dir_path):
            continue
            
        files = sorted([f for f in os.listdir(split_dir_path) if f.endswith(".dat")])
        for file_name in files:
            full_file_path = os.path.join(split_dir_path, file_name)
            
            print(f"Parsing text file structure: {file_name}...")
            
            subject_object = get_subject_data(full_file_path)
            
            docs_batch = transform_subject_to_docs(subject_object, split_name=split)
            
            for doc in docs_batch:
                doc["split"] = split
            
            if docs_batch:
                print(f"Uploading {len(docs_batch)} structured activity blocks...")
                collection.insert_many(docs_batch, ordered=False)
                print(f"Synced: {file_name}\n")

    print("Success! All eligible data has been processed and uploaded to MongoDB.")

if __name__ == "__main__":
    main()