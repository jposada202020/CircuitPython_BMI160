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


* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register

"""

import time
from micropython import const
from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import ROUnaryStruct, UnaryStruct
from adafruit_register.i2c_bits import RWBits

try:
    from busio import I2C
    from typing_extensions import NoReturn
    from typing import Tuple
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_BMI160.git"


_I2C_ADDR = const(0x69)
_REG_WHOAMI = const(0x00)
_ERROR_CODE = const(0x02)
_COMMAND = const(0x7E)
_ACCEL_CONFIG = const(0x40)
_ACC_RANGE = const(0x41)

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

# Acceleration Range
ACCEL_RANGE_2G = const(0b0011)
ACCEL_RANGE_4G = const(0b0101)
ACCEL_RANGE_8G = const(0b1000)
ACCEL_RANGE_16G = const(0b1100)

# UNDERSAMPLE
NO_UNDERSAMPLE = const(0)
UNDERSAMPLE = const(1)

# Bandwith Parameter
FILTER = const(0)
AVERAGING = const(1)

# Acceleration Data
ACC_X_LSB = const(0x12)
ACC_X_MSB = const(0x13)
ACC_Y_LSB = const(0x14)
ACC_Y_MSB = const(0x15)
ACC_Z_LSB = const(0x16)
ACC_Z_MSB = const(0x17)

# Acc Power Modes
ACC_POWER_SUSPEND = const(0x10)
ACC_POWER_NORMAL = const(0x11)
ACC_POWER_LOWPOWER = const(0x12)

# Temperature
TEMP_LSB = const(0x20)
TEMP_MSB = const(0x21)


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
            import bmi160 as BMI160

    Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()  # uses board.SCL and board.SDA
            bmi = BMI160.BMI160(i2c)

    Now you have access to the attributes

        .. code-block:: python

            accx, accy, accz = bmi.acceleration


    """

    _device_id = ROUnaryStruct(_REG_WHOAMI, "B")
    _soft_reset = UnaryStruct(_COMMAND, "B")
    _error_code = UnaryStruct(_ERROR_CODE, "B")
    _acc_config = UnaryStruct(_ACCEL_CONFIG, "B")
    _power_mode = UnaryStruct(0x03, "B")

    # Acceleration Data
    _acc_data_x_msb = UnaryStruct(ACC_X_MSB, "B")
    _acc_data_x_lsb = UnaryStruct(ACC_X_LSB, "B")
    _acc_data_y_msb = UnaryStruct(ACC_Y_MSB, "B")
    _acc_data_y_lsb = UnaryStruct(ACC_Y_LSB, "B")
    _acc_data_z_msb = UnaryStruct(ACC_Z_MSB, "B")
    _acc_data_z_lsb = UnaryStruct(ACC_Z_LSB, "B")
    _read = UnaryStruct(_COMMAND, "B")

    # ACC_CONF Register (0x40)
    # Sets the output data rate, the bandwidth, and the read mode of the acceleration
    # sensor
    _acc_us = RWBits(1, _ACCEL_CONFIG, 7)
    _acc_bwp = RWBits(1, _ACCEL_CONFIG, 6)
    _acc_odr = RWBits(4, _ACCEL_CONFIG, 0)

    # ACC_RANGE Register (0x41)
    # The register allows the selection of the accelerometer g-range
    _acc_range = RWBits(4, _ACC_RANGE, 0)
    acceleration_scale = {3: 16384, 5: 8192, 8: 4096, 12: 2048}

    # Temperature
    _temp_data_msb = UnaryStruct(TEMP_MSB, "B")
    _temp_data_lsb = UnaryStruct(TEMP_LSB, "B")

    def __init__(self, i2c_bus: I2C, address: int = _I2C_ADDR) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

        if self._device_id != 0xD1:
            raise RuntimeError("Failed to find BMI160")

        self.soft_reset()

        self._read = 0x03
        time.sleep(0.1)
        self._read = ACC_POWER_NORMAL
        time.sleep(0.1)
        self._read = 0x15
        time.sleep(0.1)
        self._read = 0x19

    def soft_reset(self) -> NoReturn:
        """
        Performs a Soft Reset

        :return: NoReturn

        """
        self._soft_reset = RESET_COMMAND
        time.sleep(0.015)

    def error_code(self) -> NoReturn:
        """
        The register is meant for debug purposes, not for regular verification
        if an operation completed successfully..

        Fatal Error: Error during bootup. Broken hardware(e.g.NVM error, see
        ASIC spec for details).This flag will not be cleared after reading the
        register.The only way to clear the flag is a POR.

        Error flags (bits 7:4) store error event until they are reset by reading the register.

        """

        code_errors = {
            0: "No Error",
            1: "Error",
            2: "Error",
            3: "low-power mode and interrupt uses pre-filtered data",
            6: "ODRs of enabled sensors in header-less mode do not match",
            7: "pre-filtered data are used in low power mode",
        }
        errors = self._error_code
        drop_cmd_err = (errors & 0x40) >> 6
        error_codes = (errors & 0x1E) >> 1
        fatal_error = errors & 0x01
        if drop_cmd_err:
            print("Drop Command Error")
        if code_errors[error_codes] != "No Error":
            print(code_errors[error_codes])
        if fatal_error:
            print("Fatal Error")

    @property
    def acceleration_undersample(self) -> int:
        """
        The undersampling parameter is typically used in low power mode.
        When acc_us is set to ‘0’ and the accelerometer is in low-power mode,
        it will change to normal mode. If the acc_us is set to ‘0’ and a
        command to enter low-power mode is sent to the Register (0x7E) CMD,
        this command is ignored.

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`BMI160.NO_UNDERSAMPLE`      | :py:const:`0`           |
        +----------------------------------------+-------------------------+
        | :py:const:`BMI160.UNDERSAMPLE`         | :py:const:`1`           |
        +----------------------------------------+-------------------------+

        """
        return self._acc_us

    @acceleration_undersample.setter
    def acceleration_undersample(self, value: int) -> NoReturn:
        self._acc_us = value

    @property
    def acceleration_bandwidth_parameter(self) -> int:
        """
        Determines filter configuration (acc_us=0) and averaging for
        undersampling mode (acc_us=1).

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`BMI160.FILTER`              | :py:const:`0`           |
        +----------------------------------------+-------------------------+
        | :py:const:`BMI160.AVERAGING`           | :py:const:`1`           |
        +----------------------------------------+-------------------------+

        """
        return self._acc_bwp

    @acceleration_bandwidth_parameter.setter
    def acceleration_bandwidth_parameter(self, value: int) -> NoReturn:
        self._acc_bwp = value

    @property
    def acceleration_output_data_rate(self) -> int:
        """
        Define the output data rate in Hz is given by :math:`100/2^(8-accodr)`
        The output data rate is independent of the power mode setting for the sensor

        Configurations without a bandwidth number are illegal settings and will
        result in an error code in the Register (0x02) ERR_REG.

        At startup this is setup at 100 Hz

        +----------------------------------------+---------------------------------+
        | Mode                                   | Value                           |
        +========================================+=================================+
        | :py:const:`BMI160.BANDWIDTH_25_32`     | :py:const:`0b0001` 25/32 Hz     |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_25_16`     | :py:const:`0b0010` 25/16 Hz     |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_25_8`      | :py:const:`0b0011` 25/8 Hz      |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_25_4`      | :py:const:`0b0100` 25/4 Hz      |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_25_2`      | :py:const:`0b0101` 25/2 Hz      |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_25`        | :py:const:`0b0110` 25 Hz        |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_50`        | :py:const:`0b0111` 50 Hz        |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_100`       | :py:const:`0b1000` 100 Hz       |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_200`       | :py:const:`0b1001` 200 Hz       |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_400`       | :py:const:`0b1010` 400 Hz       |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_800`       | :py:const:`0b1011` 800 Hz       |
        +----------------------------------------+---------------------------------+
        | :py:const:`BMI160.BANDWIDTH_1600`      | :py:const:`0b1100` 1600 Hz      |
        +----------------------------------------+---------------------------------+


        """
        return self._acc_odr

    @acceleration_output_data_rate.setter
    def acceleration_output_data_rate(self, value: int) -> NoReturn:
        self._acc_odr = value

    @property
    def acceleration_range(self) -> int:
        """
        The register allows the selection of the accelerometer g-range.
        Changing the range of the accelerometer does not clear the data
        ready bit in the Register (0x1B) STATUS. It is recommended to
        read the Register (0x04-0x17) DATA after the range change to
        remove a stall data ready bit from before the range change.

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`BMI160.ACCEL_RANGE_2G`      | :py:const:`0b0011`      |
        +----------------------------------------+-------------------------+
        | :py:const:`BMI160.ACCEL_RANGE_4G`      | :py:const:`0b0101`      |
        +----------------------------------------+-------------------------+
        | :py:const:`BMI160.ACCEL_RANGE_8G`      | :py:const:`0b1000`      |
        +----------------------------------------+-------------------------+
        | :py:const:`BMI160.ACCEL_RANGE_16G`     | :py:const:`0b1100`      |
        +----------------------------------------+-------------------------+

        """
        return self._acc_range

    @acceleration_range.setter
    def acceleration_range(self, value: int) -> NoReturn:
        self._acc_range = value

    @property
    def acceleration(self) -> Tuple[int, int, int]:

        factor = self.acceleration_scale[self.acceleration_range]

        x = (self._acc_data_x_msb * 256 + self._acc_data_x_lsb) / factor
        y = (self._acc_data_y_msb * 256 + self._acc_data_y_lsb) / factor
        z = (self._acc_data_z_msb * 256 + self._acc_data_z_lsb) / factor
        return x, y, z

    def power_mode_status(self) -> NoReturn:
        values = self._power_mode

        acc_pmu_status = (values & 0x18) >> 4
        gyr_pmu_status = (values & 0xC) >> 2
        mag_pmu_status = values & 0x03

        acc_pmu_codes = {0: "Suspend", 1: "Normal", 2: "Low Power"}
        gyr_pmu_codes = {0: "Suspend", 1: "Normal", 3: "Fast Start - Up"}
        mag_pmu_codes = {0: "Suspend", 1: "Normal", 2: "Low Power"}

        print("Acceleration Power Mode: ", acc_pmu_codes[acc_pmu_status])
        print("Gyro Power Mode", gyr_pmu_codes[gyr_pmu_status])
        print("Mag Power Mode", mag_pmu_codes[mag_pmu_status])

    def acc_power_mode(self, value: int) -> NoReturn:
        """
        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`BMI160.ACC_POWER_SUSPEND`   | :py:const:`0x10`        |
        +----------------------------------------+-------------------------+
        | :py:const:`BMI160.ACC_POWER_NORMAL`    | :py:const:`0x11`        |
        +----------------------------------------+-------------------------+
        | :py:const:`BMI160.POWER_LOWPOWER `     | :py:const:`0x12`        |
        +----------------------------------------+-------------------------+

        """
        self._read = value
        time.sleep(0.1)

    @property
    def temperature(self) -> int:
        """
        The temperature is disabled when all sensors are in suspend mode. The output
        word of the 16-bit temperature sensor is valid if the gyroscope is in normal
        mode, i.e. gyr_pmu_status=0b01. The resolution is typically :math:`1/2^9` K/LSB.

        If the gyroscope is in normal mode (see Register (0x03) PMU_STATUS),
        the temperature is updated every 10 ms (+-12%). If the gyroscope is in suspend
        mode or fast-power up mode, the temperature is updated every 1.28 s aligned
        :return: int
        """

        return ((self._temp_data_msb * 256 + self._temp_data_lsb) * 1/2**9) + 23
