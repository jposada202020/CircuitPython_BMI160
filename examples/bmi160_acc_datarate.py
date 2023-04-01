# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import board
import bmi160 as BMI160


i2c = board.I2C()  # uses board.SCL and board.SDA
bmi = BMI160.BMI160(i2c)

print("Current Acceleration data rate", bmi.acceleration_output_data_rate)
print("Changing Acceleration data rate to 25/32 Hz")
bmi.acceleration_output_data_rate = BMI160.BANDWIDTH_25_32
print("Changed Acceleration data rate", bmi.acceleration_output_data_rate)
print("Changing Acceleration data rate to 12.5 Hz")
bmi.acceleration_output_data_rate = BMI160.BANDWIDTH_25_2
print("Changed Acceleration data rate", bmi.acceleration_output_data_rate)
print("Changing Acceleration data rate to 800")
bmi.acceleration_output_data_rate = BMI160.BANDWIDTH_800
print("Changed Acceleration data rate", bmi.acceleration_output_data_rate)
