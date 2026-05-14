from numpy import nan


class Vector3:
    x: float
    y: float
    z: float
    def __init__(self, x: float, y, float, z: float):
        self.x = x
        self.y = y
        self.z = z


class IMUSensoryData:
    temperature: float
    accelerometer_16: Vector3
    accelerometer_6: Vector3
    gyroscope: Vector3
    magnetometer: Vector3
    def __init__(self, temperature: float, accelerometer_16: Vector3, accelerometer_6: Vector3, gyroscope: Vector3, magnetometer: Vector3):
        self.temperature = temperature
        self.accelerometer_16 = accelerometer_16
        self.accelerometer_6 = accelerometer_6
        self.gyroscope = gyroscope
        self.magnetometer = magnetometer


class SubjectRow:
    timestamp: float
    activity: float
    # heart_rate: float
    imu_hand: IMUSensoryData
    imu_chest: IMUSensoryData
    imu_ankle: IMUSensoryData
    def __init__(self, timestamp: float, activity: float, imu_hand: IMUSensoryData, imu_chest: IMUSensoryData, imu_ankle: IMUSensoryData):
        self.timestamp = timestamp
        self.activity = activity
        self.imu_hand = imu_hand
        self.imu_chest = imu_chest
        self.imu_ankle = imu_ankle


class SubjectData:
    id: int
    data_rows: list[SubjectRow]
    def __init__(self, id: int, data_rows: list[SubjectData]):
        self.id = id
        self.data_rows = data_rows