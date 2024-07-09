"""Multisensor main module.

This module implements a class for managing multiple identical I2C
of the same type using the same I2C bus.
Multiple identical devices are using the same address after reset,
which is causing bus conflict.
The solution is to reallocate them to different addresses
while taking them out of reset one by one.
"""

import time
import sys

import board
import busio

import adafruit_vl6180x

try:
    from RPi import GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Superuser privileges required!")
    sys.exit(1)

# Register for changing the device bus address
SUBORDINATE_ADDR_REG = 0x212


class MultiSensor:
    """Manage multiple I2C sensors of the same kind on the same bus."""

    def __init__(
        self,
        ce_gpios: list,
        new_i2c_addresses: list,
        offsets: list = None,
        mode_gpio=GPIO.BCM,
        default_i2c_address=0x29,
    ):
        """
        Initialize the MultiSensor instance.

        Parameters:
        - ce_gpios (list[int]): GPIO pin numbers used to control each sensor.
        - new_i2c_addresses (list[int]): New I2C addresses to assign to each sensor.
        - offsets (list[int], optional): Offset values for each sensor (default is None).
        - mode_gpio (int, optional): GPIO mode to use (GPIO.BCM or GPIO.BOARD, default is GPIO.BCM).
        - default_i2c_address (int, optional): Default I2C address for sensors (default is 0x29).

        Raises:
        - AssertionError: If inputs are invalid or inconsistent.
        - OSError: If there is an I/O error during initialization.

        """


        #Control parameters
        assert isinstance(ce_gpios, list), "ce_gpios must be a list"
        assert isinstance(new_i2c_addresses, list), "new_i2c_addresses must be a list"
        assert len(ce_gpios) == len(
            new_i2c_addresses
        ), "ce_gpios and new_i2c_addresses must be the same size"
        assert isinstance(offsets, list), "offsets must be a list"

        if offsets is None:
            offsets = [0] * len(ce_gpios)

        assert len(ce_gpios) == len(
            offsets
        ), "ce_gpios and offsets must be the same size"
        assert all(
            0 <= addr <= 127 for addr in new_i2c_addresses
        ), "new_i2c_addresses must be in the range 0-127 inclusive"
        assert mode_gpio in (
            GPIO.BCM,
            GPIO.BOARD,
        ), "mode_gpio must be GPIO.BCM or GPIO.BOARD"
        assert isinstance(
            default_i2c_address, int
        ), "default_i2c_address must be an int"
        assert (
            0 <= default_i2c_address <= 127
        ), "default_i2c_address must be in the range 0-127 inclusive"


        #Instance sensors
        try:
            GPIO.setmode(mode_gpio)
            GPIO.setup(ce_gpios, GPIO.OUT)
            GPIO.output(ce_gpios, GPIO.LOW)
            self.sensors = self._realloc_addr(
                ce_gpios, new_i2c_addresses, offsets, default_i2c_address
            )
        except Exception as e:
            print(f"Initialization error: {e}")
            raise

    def _realloc_addr(self, channels, i2c_addresses, offsets, default_i2c_address):
        """
        Reallocate default I2C addresses for sensors.

        All the sensors are now shut down (done in the constructor).
        Turn them on one by one and reassign to another address.

        Parameters:
        - channels (list[int]): GPIO pin numbers for each sensor.
        - i2c_addresses (list[int]): New I2C addresses to assign to each sensor.
        - offsets (list[int]): Offset values for each sensor.
        - default_i2c_address (int): Default I2C address for sensors.

        Returns:
        - list[adafruit_vl6180x.VL6180X]: List of initialized sensor instances.

        """
        i2c = busio.I2C(board.SCL, board.SDA)
        busy_addr = i2c.scan()
        print(
            f"address i2c detect: {", ".join([f"0x{addr:02x}" for addr in busy_addr])}"
        )

        working_address = {
            i2c_address: channel
            for i2c_address, channel in zip(i2c_addresses, channels)
            if i2c_address not in busy_addr
        }

        for i2c_address, channel in working_address.items():
            print(f"Create new address 0x{i2c_address:02x}, in channel {channel}")
            # Turn on the sensor to change address
            GPIO.output(channel, GPIO.HIGH)

            # Hitting an error without this delay
            # Adafruit_PureIO/smbus.py", line 308, in write_bytes
            # self._device.write(buf) OSError:
            # [Errno 121] Remote I/O error
            time.sleep(0.1)

            try:
                # Instantiate as temporary
                temp = adafruit_vl6180x.VL6180X(i2c, address=default_i2c_address)

                # Change the address to the assigned one
                temp._write_8(SUBORDINATE_ADDR_REG, i2c_address)
            except OSError as e:
                print(
                    f"Error initializing sensor at address 0x{i2c_address:02X} and channel {{channel}}: {e}"
                )

        sensors = []
        # Instantiate all sensors with their final addresses
        for i2c_address, offset in zip(i2c_addresses, offsets):
            try:
                sensor = adafruit_vl6180x.VL6180X(
                    i2c, address=i2c_address, offset=offset
                )
                sensors.append(sensor)
            except OSError as e:
                print(f"Error initializing sensor at address 0x{i2c_address:02X}: {e}")

        return sensors

    def get_range(self, idx_sensor):
        """
        Get the range from a specific sensor.

        Parameters:
        - idx_sensor (int): Index of the sensor to retrieve the range from.

        Returns:
        - int: Range of the specified sensor in millimeters, or None if the sensor index is invalid.

        """
        try:
            return self.sensors[idx_sensor].range
        except IndexError:
            print(f"Invalid sensor index: {idx_sensor}")
            return None
        except Exception as e:
            print(f"Error retrieving range from sensor {idx_sensor}: {e}")
            return None

    def get_lux(self, idx_sensor, gain: int) -> float:
        """
        Get the lux value from a specific sensor.

        Parameters:
        - idx_sensor (int): Index of the sensor to retrieve the lux value from.
        - gain (int): Gain value to use for lux measurement.

        Returns:
        - float: Lux value of the specified sensor, or None if the sensor index is invalid.

        """
        try:
            return self.sensors[idx_sensor].read_lux(gain)
        except IndexError:
            print(f"Invalid sensor index: {idx_sensor}")
        except Exception as e:
            print(f"Error retrieving lux value from sensor {idx_sensor}: {e}")
        return None

    def get_range_status(self, idx_sensor: int) -> int:
        """
        Get the range status from a specific sensor.

        Parameters:
        - idx_sensor (int): Index of the sensor to retrieve the range status from.

        Returns:
        - int: Range status of the specified sensor, or None if the sensor index is invalid.

        """
        try:
            return self.sensors[idx_sensor].range_status
        except IndexError:
            print(f"Invalid sensor index: {idx_sensor}")
        except Exception as e:
            print(f"Error retrieving range status from sensor {idx_sensor}: {e}")
        return None
