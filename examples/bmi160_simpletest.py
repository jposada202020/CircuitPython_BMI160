# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import board
import bmi160


i2c = board.I2C()  # uses board.SCL and board.SDA
isl = bmi160.BMI160(i2c)
