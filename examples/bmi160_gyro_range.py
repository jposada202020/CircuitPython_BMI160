# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import board
import bmi160 as BMI160


i2c = board.I2C()  # uses board.SCL and board.SDA
bmi = BMI160.BMI160(i2c)

print("Current Gyro Range", bmi.gyro_range)
print("Gyro Values x, y, z", bmi.gyro)
print("Changing Gyro Range to 2000")
bmi.acceleration_range = BMI160.GYRO_RANGE_2000
print("Changed Gyro Range", bmi.gyro_range)
print("Gyro Values x, y, z", bmi.gyro)
print("Changing Gyro Range to 500")
bmi.acceleration_range = BMI160.GYRO_RANGE_500
print("Changed Gyro Range", bmi.gyro_range)
print("Gyro Values x, y, z", bmi.gyro)
print("Changing Gyro Range to 125")
bmi.acceleration_range = BMI160.GYRO_RANGE_125
print("Changed Gyro Range", bmi.gyro_range)
print("Gyro Values x, y, z", bmi.gyro)
