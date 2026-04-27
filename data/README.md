# Data local repository

**This folder holds the dataset that feeds the rest of the project.** The 
hardware that the project was originally built around (the Mbientlab 
MetaMotionR wristband) is not available for this offering, so you will work 
with the **PAMAP2 Physical Activity Monitoring** dataset instead. Download data from here: [PAMAP2](https://archive.ics.uci.edu/dataset/231/pamap2+physical+activity+monitoring)

## Folder layout

```
data/
├── README.md                  (this file)
└── PAMAP2_Dataset/
    ├── readme.pdf                     (canonical dataset description — read this first)
    ├── DataCollectionProtocol.pdf
    ├── DescriptionOfActivities.pdf
    ├── PerformedActivitiesSummary.pdf
    ├── subjectInformation.pdf
    ├── Protocol/                      (9 subjects, all required activities)
    │   ├── subject101.dat
    │   ├── ...
    │   └── subject109.dat
    └── Optional/                      (5 subjects, additional activities)
        ├── subject101.dat
        ├── ...
        └── subject109.dat
```

Do **not** rename or restructure the `PAMAP2_Dataset/` directory — your code 
should read it in place.

## Raw `.dat` file format

Each `.dat` file is a space-separated text file with **54 columns** sampled 
at **100 Hz**. Column groups (1-indexed, as in the PAMAP2 readme):

| Columns | Content                                                     |
|---------|-------------------------------------------------------------|
| 1       | timestamp (seconds)                                         |
| 2       | activity ID (see the table in the root `README.md`)         |
| 3       | heart rate (bpm) — **do not use**, sampled at 9 Hz          |
| 4–20    | IMU **hand/wrist**: temperature, acc±16g, acc±6g, gyro, mag, orientation |
| 21–37   | IMU **chest**: same layout                                  |
| 38–54   | IMU **ankle**: same layout                                  |

For each IMU, use the **±16g accelerometer** (3 axes) and the **gyroscope** 
(3 axes) as the default channels. The orientation columns are flagged as 
invalid in the dataset documentation — ignore them. Heart rate and any other 
biometric channel are out of scope for this project.

Missing samples (dropped wireless packets) are encoded as `NaN` and must be 
handled explicitly during preprocessing.

## Ingestion pipeline

The data flow is:

```
.dat files  ──parse──▶  per-(subject, activity) segments  ──insert──▶  MongoDB  ──fetch──▶  notebooks
```

Concretely:

1. Read each `.dat` file with `pandas` (whitespace-delimited, no header).
2. Drop rows with `activity_id == 0` (transient periods between activities).
3. Group the remaining rows by `(subject_id, activity_id)` into contiguous 
   recording segments.
4. Restrict columns to the IMU channels you decided to use (start with the 
   hand/wrist accelerometer and gyroscope only — see "Sensor Selection 
   Strategy" in the root `README.md`).
5. Convert each segment into a MongoDB document using the schema below and 
   insert it into your collection.
6. From the analysis notebooks, **fetch documents from MongoDB** rather than 
   re-reading the raw files.

## MongoDB document schema

Each MongoDB document corresponds to one contiguous segment of one activity 
performed by one subject. The default schema (hand/wrist IMU, accelerometer 
+ gyroscope) is:

```json
{
  "_id": ObjectId("6984b3fa87abe7f4dff571aa"),
  "data": {
    "acc_x": ["array", "of", "values"],
    "acc_y": ["array", "of", "values"],
    "acc_z": ["array", "of", "values"],
    "gyr_x": ["array", "of", "values"],
    "gyr_y": ["array", "of", "values"],
    "gyr_z": ["array", "of", "values"]
  },
  "activity_id": 4,
  "activity_label": "walking",
  "subject": "101",
  "split": "Protocol",
  "imu_location": "hand",
  "sensor": "AccGyr",
  "sr": 100,
  "datetime": "MongoDB datetime object (it can be generated with the datetime.datetime.now() function)"
}
```

Field notes:

* `activity_id` — the integer label as it appears in the `.dat` file. 
  `activity_label` is the human-readable name from the activity table in the 
  root `README.md`.
* `subject` — the file's subject identifier (e.g. `"101"` … `"109"`).
* `split` — `"Protocol"` or `"Optional"`, matching the source subdirectory.
* `imu_location` — `"hand"`, `"chest"`, or `"ankle"`. Use one document per 
  IMU location; do **not** concatenate IMUs into a single document.
* `sensor` — `"Acc"`, `"Gyr"`, or `"AccGyr"`. If you later expand to the 
  magnetometer, use `"AccGyrMag"` and add `mag_x`, `mag_y`, `mag_z` keys 
  using the same axis order convention.
* `sr` — sampling rate in Hz. Must be `100` (downsample any channel that 
  isn't natively at 100 Hz before inserting).

If you are using only the gyroscope for an experiment, drop the `acc_*` keys 
and keep `gyr_x`, `gyr_y`, `gyr_z`. The same axis-naming convention applies 
to the accelerometer-only case (`acc_x`, `acc_y`, `acc_z`).

## Quick reference — activity labels

See the activity tables in the root `README.md`. Activity ID `0` is 
*transient* and must be excluded before insertion.
