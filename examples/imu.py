from pupil_labs.neon_usb import IMU

imu = IMU()

while True:
    imu_datum = imu.get_imu_data()
    print(f"Timestamp: {imu_datum.timestamp_unix_seconds}")
    print(f"Gyro: {imu_datum.gyro_data}")
    print(f"Accel: {imu_datum.accel_data}")
    print(f"Quaternion: {imu_datum.quaternion}")
    print("---")
