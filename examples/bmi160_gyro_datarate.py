# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import board
import bmi160 as BMI160


i2c = board.I2C()  # uses board.SCL and board.SDA
bmi = BMI160.BMI160(i2c)

print("Current Gyro data rate", bmi.gyro_output_data_rate)
print("Changing Gyro data rate to 25 Hz")
bmi.gyro_output_data_rate = BMI160.BANDWIDTH_25
print("Changed Gyro data rate", bmi.gyro_output_data_rate)
print("Changing Gyro data rate to 200 Hz")
bmi.gyro_output_data_rate = BMI160.BANDWIDTH_200
print("Changed Gyro data rate", bmi.gyro_output_data_rate)
print("Changing Gyro data rate to 800")
bmi.gyro_output_data_rate = BMI160.BANDWIDTH_800
print("Changed Gyro data rate", bmi.gyro_output_data_rate)
