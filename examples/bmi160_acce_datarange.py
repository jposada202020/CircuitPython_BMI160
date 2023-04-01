# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import board
import bmi160 as BMI160


i2c = board.I2C()  # uses board.SCL and board.SDA
bmi = BMI160.BMI160(i2c)

print("Current Acceleration Range", bmi.acceleration_range)
print("Acceleration Values x, y, z", bmi.acceleration)
print("Changing Acceleration Range to 4G")
bmi.acceleration_range = BMI160.ACCEL_RANGE_4G
print("Changed Acceleration Range", bmi.acceleration_range)
print("Acceleration Values x, y, z", bmi.acceleration)
print("Changing Acceleration Range to 8G")
bmi.acceleration_range = BMI160.ACCEL_RANGE_8G
print("Changed Acceleration Range", bmi.acceleration_range)
print("Acceleration Values x, y, z", bmi.acceleration)
print("Changing Acceleration Range to 8G")
bmi.acceleration_range = BMI160.ACCEL_RANGE_16G
print("Changed Acceleration Range", bmi.acceleration_range)
print("Acceleration Values x, y, z", bmi.acceleration)
