# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import bmi160


i2c = board.I2C()  # uses board.SCL and board.SDA
isl = bmi160.BMI160(i2c)

accx, accy, accz = isl.acceleration

while True:
    accx, accy, accz = isl.acceleration
    print("Acceleration X: ", accx)
    print("Acceleration Y: ", accy)
    print("Acceleration Z: ", accz)
    time.sleep(0.5)
