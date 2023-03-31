# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`bmi160`
================================================================================

Driver for the BMI160 sensor


* Author(s): Jose D. Montoya

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads


# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

import time
from micropython import const
from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import ROUnaryStruct, UnaryStruct
from adafruit_register.i2c_bits import RWBits

try:
    from busio import I2C
    from typing_extensions import NoReturn
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_BMI160.git"


_I2C_ADDR = const(0x69)
_REG_WHOAMI = const(0x00)
_ERROR_CODE = const(0x02)
_COMMAND = const(0x7E)
_ACCEL_CONFIG = const(0x40)

# RESET Command
RESET_COMMAND = const(0xB6)

# Acceleration Output Rate HZ
BANDWIDTH_25_32 = const(0b0001)  # 25/32 Hz
BANDWIDTH_25_16 = const(0b0010)  # 25/16 Hz
BANDWIDTH_25_8 = const(0b0011)  # 25/8 Hz
BANDWIDTH_25_4 = const(0b0100)  # 25/4 Hz
BANDWIDTH_25_2 = const(0b0101)  # 25/2 Hz
BANDWIDTH_25 = const(0b0110)  # 25 Hz
BANDWIDTH_50 = const(0b0111)  # 50 Hz
BANDWIDTH_100 = const(0b1000)  # 100 Hz
BANDWIDTH_200 = const(0b1001)  # 200 Hz
BANDWIDTH_400 = const(0b1010)  # 400 Hz
BANDWIDTH_800 = const(0b1011)  # 800 Hz
BANDWIDTH_1600 = const(0b1100)  # 1600 Hz

# UNDERSAMPLE
NO_UNDERSAMPLE = const(0)
UNDERSAMPLE = const(1)

# Bandwith Parameter
FILTER = const(0)
AVERAGING = const(1)


# pylint: disable= invalid-name, too-many-instance-attributes, missing-function-docstring


class BMI160:
    """Driver for the BMI160 Sensor connected over I2C.

    :param ~busio.I2C i2c_bus: The I2C bus the BMI160 is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x69`

    :raises RuntimeError: if the sensor is not found

    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`BMI160` class.
    First you will need to import the libraries to use the sensor

        .. code-block:: python

            import board
            import circuitpython_BMI160.BMI160 as BMI160

    Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()  # uses board.SCL and board.SDA
            isl = BMI160.BMI160(i2c)

    Now you have access to the attributes

        .. code-block:: python

            TODO: XXXXXXXXXXXXXXXXXXXXXX


    """

    _device_id = ROUnaryStruct(_REG_WHOAMI, "B")
    _soft_reset = UnaryStruct(_COMMAND, "B")
    _error_code = UnaryStruct(_ERROR_CODE, "B")
    _acc_config = UnaryStruct(_ACCEL_CONFIG, "B")

    # ACC_CONF Register (0x40)
    # Sets the output data rate, the bandwidth, and the read mode of the acceleration
    # sensor
    _acc_us = RWBits(1, _ACCEL_CONFIG, 7)
    _acc_bwp = RWBits(1, _ACCEL_CONFIG, 6)
    _acc_odr = RWBits(4, _ACCEL_CONFIG, 0)

    def __init__(self, i2c_bus: I2C, address: int = _I2C_ADDR) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

        if self._device_id != 0xD1:
            raise RuntimeError("Failed to find BMI160")

        self.soft_reset()
        print(self.acceleration_output_data_rate)
        print(bin(self._error_code))

    def soft_reset(self) -> NoReturn:
        """
        Performs a Soft Reset

        :return: NoReturn

        """
        self._soft_reset = RESET_COMMAND
        time.sleep(0.015)

    @property
    def acceleration_undersample(self):
        """
        The undersampling parameter is typically used in low power mode.
        When acc_us is set to ‘0’ and the accelerometer is in low-power mode,
        it will change to normal mode. If the acc_us is set to ‘0’ and a
        command to enter low-power mode is sent to the Register (0x7E) CMD,
        this command is ignored.

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`BMI.NO_UNDERSAMPLE`         | :py:const:`0`           |
        +----------------------------------------+-------------------------+
        | :py:const:`BMI.UNDERSAMPLE`            | :py:const:`1`           |
        +----------------------------------------+-------------------------+

        """
        return self._acc_us

    @acceleration_undersample.setter
    def acceleration_undersample(self, value: int):
        self.acceleration_undersample = value

    @property
    def acceleration_bandwidth_parameter(self):
        """
        Determines filter configuration (acc_us=0) and averaging for
        undersampling mode (acc_us=1).

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`BMI.FILTER`                 | :py:const:`0`           |
        +----------------------------------------+-------------------------+
        | :py:const:`BMI.AVERAGING`              | :py:const:`1`           |
        +----------------------------------------+-------------------------+

        """
        return self._acc_bwp

    @acceleration_bandwidth_parameter.setter
    def acceleration_bandwidth_parameter(self, value: int):
        self.acceleration_bandwidth_parameter = value

    @property
    def acceleration_output_data_rate(self):
        """
        Define the output data rate in Hz is given by :math:`100/2^(8-accodr)`
        The output data rate is independent of the power mode setting for the sensor

        Configurations without a bandwidth number are illegal settings and will
        result in an error code in the Register (0x02) ERR_REG.

        +----------------------------------------+---------------------------------+
        | Mode                                   | Value                           |
        +========================================+=================================+
        | :py:const:`BMI.BANDWIDTH_25_32`        | :py:const:`0b0001` 25/32 Hz     |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_25_16`        | :py:const:`0b0010` 25/16 Hz     |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_25_8`         | :py:const:`0b0011` 25/8 Hz      |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_25_4`         | :py:const:`0b0100` 25/4 Hz      |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_25_2`         | :py:const:`0b0101` 25/2 Hz      |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_25`           | :py:const:`0b0110` 25 Hz        |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_50`           | :py:const:`0b0111` 50 Hz        |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_100`          | :py:const:`0b1000` 100 Hz       |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_200`          | :py:const:`0b1001` 200 Hz       |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_400`          | :py:const:`0b1010` 400 Hz       |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_800`          | :py:const:`0b1011` 800 Hz       |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI.BANDWIDTH_1600`         | :py:const:`0b1100` 1600 Hz      |
        +----------------------------------------+---------------------------------+


        """
        return self._acc_odr

    @acceleration_output_data_rate.setter
    def acceleration_output_data_rate(self, value: int):
        self.acceleration_output_data_rate = value
