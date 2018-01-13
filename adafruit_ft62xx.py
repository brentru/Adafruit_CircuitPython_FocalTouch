# The MIT License (MIT)
#
# Copyright (c) 2017 ladyada for adafruit industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_ft62xx`
====================================================

TODO(description)

* Author(s): ladyada
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_ft62xx.git"

try:
    import struct
except ImportError:
    import ustruct as struct

from adafruit_bus_device.i2c_device import I2CDevice

from micropython import const


_FT6206_DEFAULT_I2C_ADDR = 0x38

_FT6206_REG_DATA = 0x00
_FT6206_REG_NUMTOUCHES = 0x02
_FT6206_REG_FACTORYMODE = 0x40
_FT6206_REG_THRESHHOLD = 0x80
_FT6206_REG_POINTRATE = 0x88
_FT6206_REG_FIRMVERS = 0xA6
_FT6206_REG_CHIPID = 0xA3
_FT6206_REG_VENDID = 0xA8

class Adafruit_FT6206:
    """
    A driver for the FocalTech capacitive touch sensor.
    """

    _debug = False
    
    def __init__(self, i2c, address=_FT6206_DEFAULT_I2C_ADDR, debug=False):
        self._i2c = I2CDevice(i2c, address)
        self._debug = debug

        if self._read(_FT6206_REG_VENDID, 1)[0] != 17 or self._read(_FT6206_REG_CHIPID, 1)[0] != 6:
            raise RuntimeError("Did not find FT6206 chip")

        if debug:
            print("Firmware vers %d" % self._read(_FT6206_REG_FIRMVERS, 1)[0])
            print("Point rate %d Hz" % self._read(_FT6206_REG_POINTRATE, 1)[0])
            print("Thresh %d" % self._read(_FT6206_REG_THRESHHOLD, 1)[0])

    @property
    def touched(self):
         return self._read(_FT6206_REG_NUMTOUCHES, 1)[0]

    @property
    def touches(self):
        touchpoints = []
        data = self._read(_FT6206_REG_DATA, 32)

        for t in range(2):
            point_data = data[t*6+3 : t*6+9]
            if all([i == 0xFF for i in point_data]):
                continue
            #print([hex(i) for i in point_data])
            x, y, weight, misc = struct.unpack('>HHBB', point_data)
            #print(x, y, weight, misc)
            touch_id = y >> 12
            x &= 0xFFF
            y &= 0xFFF
            point = {'x':x , 'y': y, 'id': touch_id}
            touchpoints.append(point)
        return touchpoints

    def _read(self, register, length):
        """Returns an array of 'length' bytes from the 'register'"""
        with self._i2c as i2c:
            i2c.write(bytes([register & 0xFF]))
            result = bytearray(length)
            i2c.readinto(result)
            if self._debug:
                print("\t$%02X => %s" % (register, [hex(i) for i in result]))
            return result

    def _write(self, register, values):
        """Writes an array of 'length' bytes to the 'register'"""
        with self._i2c as i2c:
            values = [(v & 0xFF) for v in [register]+values]
            i2c.write(bytes(values))
            if self._debug:
                print("\t$%02X <= %s" % (values[0], [hex(i) for i in values[1:]]))

