from numpy import float64


class Vector3:
    x: float64
    y: float64
    z: float64
    
    def __init__(self, x: float64, y: float64, z: float64):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self) -> str:
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"


class IMUSensoryData:
    temperature: float64
    accelerometer_16: Vector3
    accelerometer_6: Vector3
    gyroscope: Vector3
    magnetometer: Vector3
    
    def __init__(self, temperature: float64, accelerometer_16: Vector3, accelerometer_6: Vector3, gyroscope: Vector3, magnetometer: Vector3):
        self.temperature = temperature
        self.accelerometer_16 = accelerometer_16
        self.accelerometer_6 = accelerometer_6
        self.gyroscope = gyroscope
        self.magnetometer = magnetometer


class SubjectRow:
    timestamp: float64
    activity: float64
    # heart_rate: float64
    imu_hand: IMUSensoryData
    imu_chest: IMUSensoryData
    imu_ankle: IMUSensoryData
    
    def __init__(self, timestamp: float64, activity: float64, imu_hand: IMUSensoryData, imu_chest: IMUSensoryData, imu_ankle: IMUSensoryData):
        self.timestamp = timestamp
        self.activity = activity
        self.imu_hand = imu_hand
        self.imu_chest = imu_chest
        self.imu_ankle = imu_ankle
    
    def __str__(self):
        return_str: str = ""
        return_str += "timestamp\tactivity\timu_hand\t\t\t\t\timu_chest\t\t\t\t\timu_ankle\n"
        return_str += str(self.timestamp) + "\t\t" + str(self.activity) + "\t\ttemperature:\t" + str(self.imu_hand.temperature) + "\t\t\t\ttemperature:\t" + str(self.imu_ankle.temperature) + "\t\t\t\ttemperature:\t" + str(self.imu_ankle.temperature) + "\n"
        return_str += "\t\t\t\tacc_16:\t" + str(self.imu_hand.accelerometer_16) + "\t\tacc_16:\t" + str(self.imu_chest.accelerometer_16) + "\t\tacc_16:\t" + str(self.imu_ankle.accelerometer_16) + "\n"
        return_str += "\t\t\t\tacc_6:\t" + str(self.imu_hand.accelerometer_6) + "\t\tacc_6:\t" + str(self.imu_chest.accelerometer_6) + "\t\tacc_6:\t" + str(self.imu_ankle.accelerometer_6) + "\n"
        return_str += "\t\t\t\tgyro:\t" + str(self.imu_hand.gyroscope) + "\tgyro:\t" + str(self.imu_chest.gyroscope) + "\tgyro:\t" + str(self.imu_ankle.gyroscope) + "\n"
        return_str += "\t\t\t\tmag:\t" + str(self.imu_hand.magnetometer) + "\t\tmag:\t" + str(self.imu_chest.magnetometer) + "\t\tmag:\t" + str(self.imu_ankle.magnetometer)
        return return_str



class SubjectData:
    id: int
    data_rows: list[SubjectRow]
    
    def __init__(self, id: int, data_rows: list[SubjectRow]):
        self.id = id
        self.data_rows = data_rows