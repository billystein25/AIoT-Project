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
                IMUSensoryData(
                    # temp, acc_16,                         acc_6
                    row[3], Vector3(row[4], row[5], row[6]), Vector3(row[7], row[8], row[9]),
                    # gyro,                             mag
                    Vector3(row[10], row[11], row[12]), Vector3(row[13], row[14], row[15])
                ),
                # imu_chest:
                IMUSensoryData(
                    # temp, acc_16,                             acc_6
                    row[20], Vector3(row[21], row[22], row[23]), Vector3(row[24], row[25], row[26]),
                    # gyro,                             mag
                    Vector3(row[27], row[28], row[29]), Vector3(row[30], row[31], row[32])
                ),
                # imu_ankle:
                IMUSensoryData(
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
