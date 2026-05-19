from imu import *
import pandas as pd
from pandas import DataFrame
from numpy import ndarray
import os


def get_subject_id(filename: str) -> int:
    """
    Returns the id of the subject as an integer. Assumes the name of the file ends in '*XXX.dat'
    """
    filename = filename[:-4]
    return int(filename[-3:])


def get_data_rows(file: str) -> list[SubjectRow]:
    """
    Parses a .dat file and returns a list of SubjectRow's.
    """

    dat: DataFrame = pd.read_csv(file, sep=" ")
    npdat: ndarray = dat.to_numpy()
    
    subject_rows: list[SubjectRow] = []
    for row in npdat:
        if row[1] == 0: continue # ignore rows with activity = 0
        subject_rows.append(
            SubjectRow(
                # timestamp, activity
                row[0], row[1],
                # imu_hand:
                IMUSensorData(
                    # temp, acc_16,                         acc_6
                    row[3], Vector3(row[4], row[5], row[6]), Vector3(row[7], row[8], row[9]),
                    # gyro,                             mag
                    Vector3(row[10], row[11], row[12]), Vector3(row[13], row[14], row[15])
                ),
                # imu_chest:
                IMUSensorData(
                    # temp, acc_16,                             acc_6
                    row[20], Vector3(row[21], row[22], row[23]), Vector3(row[24], row[25], row[26]),
                    # gyro,                             mag
                    Vector3(row[27], row[28], row[29]), Vector3(row[30], row[31], row[32])
                ),
                # imu_ankle:
                IMUSensorData(
                    # temp, acc_16,                             acc_6
                    row[37], Vector3(row[38], row[39], row[40]), Vector3(row[41], row[42], row[43]),
                    # gyro,                             mag
                    Vector3(row[44], row[45], row[46]), Vector3(row[47], row[48], row[49])
                )
            )
        )
    return subject_rows


def get_subject_data(file: str) -> SubjectData:
    """
    Parses and returns all the data of the .dat file as a SubjectData object.
    """
    data_ls: list[SubjectRow] = get_data_rows(file)
    return SubjectData(get_subject_id(file), data_ls)


def get_all_subjects_in_dir(dir: str) -> list[SubjectData]:
    """
    Parses and returns all the .dat files in 'dir' as a list of SubjectData objects.
    """
    files: list[str] = [os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    
    return_ls: list[SubjectData] = []
    for file in files:
        return_ls.append(get_subject_data(file))
    
    return return_ls
from datetime import datetime

def transform_subject_to_docs(subject_data: SubjectData) -> list[dict]:
    """
    Groups raw sequential rows into per-activity segments for the HAND IMU only
    and outputs them matching the exact target MongoDB document schema.
    """
    documents = []
    
    if not subject_data.data_rows:
        return documents

    # Map to translate PAMAP2 activity IDs to labels
    activity_labels = {
        1: "lying", 2: "sitting", 3: "standing", 4: "walking", 
        5: "running", 6: "cycling", 7: "Nordic walking",
        12: "ascending stairs", 13: "descending stairs", 
        16: "vacuum cleaning", 17: "ironing", 24: "rope jumping"
    }

    # Group the rows into continuous activity blocks
    segments = []
    current_activity = subject_data.data_rows[0].activity
    current_block = []

    for row in subject_data.data_rows:
        if row.activity == current_activity:
            current_block.append(row)
        else:
            # Activity changed! Save the finished block and start a new one
            segments.append((current_activity, current_block))
            current_activity = row.activity
            current_block = [row]
            
    # Capture the final block
    if current_block:
        segments.append((current_activity, current_block))

    # Build the specialized schema for each continuous segment (HAND only)
    for activity_id, block_rows in segments:
        label = activity_labels.get(int(activity_id), "unknown")
        
        # Initialize lists to accumulate the hand sensor arrays
        acc_x, acc_y, acc_z = [], [], []
        gyr_x, gyr_y, gyr_z = [], [], []
        
        for row in block_rows:
            imu = row.imu_hand  
            
            # Append coordinates to their respective series
            acc_x.append(imu.accelerometer_16.x)
            acc_y.append(imu.accelerometer_16.y)
            acc_z.append(imu.accelerometer_16.z)
            gyr_x.append(imu.gyroscope.x)
            gyr_y.append(imu.gyroscope.y)
            gyr_z.append(imu.gyroscope.z)
       
        doc = {
            "data": {
                "acc_x": acc_x,
                "acc_y": acc_y,
                "acc_z": acc_z,
                "gyr_x": gyr_x,
                "gyr_y": gyr_y,
                "gyr_z": gyr_z
            },
            "activity_id": int(activity_id),
            "activity_label": label,
            "subject": str(subject_data.id),
            "split": "Protocol",
            "imu_location": "hand",
            "sensor": "AccGyr",
            "sr": 100,
            "datetime": datetime.now() 
        }
        documents.append(doc)
            
    return documents