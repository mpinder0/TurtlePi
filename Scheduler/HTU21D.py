import struct, array, time, io, fcntl
from threading import Lock
from abstractdataprovider import AbstractDataProvider

I2C_SLAVE = 0x0703
HTU21D_ADDR = 0x40
CMD_READ_TEMP_HOLD = "\xE3"
CMD_READ_HUM_HOLD = "\xE5"
CMD_READ_TEMP_NOHOLD = "\xF3"
CMD_READ_HUM_NOHOLD = "\xF5"
CMD_WRITE_USER_REG = "\xE6"
CMD_READ_USER_REG = "\xE7"
CMD_SOFT_RESET = "\xFE"


class i2c(object):
    def __init__(self, device, bus):
        self.fr = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
        self.fw = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)

        # set device address

        fcntl.ioctl(self.fr, I2C_SLAVE, device)
        fcntl.ioctl(self.fw, I2C_SLAVE, device)

    def write(self, bytes):
        self.fw.write(bytes)

    def read(self, bytes):
        return self.fr.read(bytes)

    def close(self):
        self.fw.close()
        self.fr.close()


class HTU21D(AbstractDataProvider):
    _lock = Lock()

    def __init__(self):
        self.dev = i2c(HTU21D_ADDR, 1)  #HTU21D 0x40, bus 1
        self.dev.write(CMD_SOFT_RESET)  #soft reset
        time.sleep(.1)

    def ctemp(self, sensorTemp):
        tSensorTemp = sensorTemp / 65536.0
        return -46.85 + (175.72 * tSensorTemp)

    def chumid(self, sensorHumid):
        tSensorHumid = sensorHumid / 65536.0
        return -6.0 + (125.0 * tSensorHumid)

    def crc8check(self, value):
        # Ported from Sparkfun Arduino HTU21D Library: https://github.com/sparkfun/HTU21D_Breakout
        remainder = ( ( value[0] << 8 ) + value[1] ) << 8
        remainder |= value[2]

        # POLYNOMIAL = 0x0131 = x^8 + x^5 + x^4 + 1
        # divsor = 0x988000 is the 0x0131 polynomial shifted to farthest left of three bytes
        divsor = 0x988000

        for i in range(0, 16):
            if ( remainder & 1 << (23 - i) ):
                remainder ^= divsor
            divsor = divsor >> 1

        if remainder == 0:
            return True
        else:
            return False

    def read_temperature(self):
        with self._lock:
            self.dev.write(CMD_READ_TEMP_NOHOLD)  #measure temp
            time.sleep(.1)

            data = self.dev.read(3)
            buf = array.array('B', data)

            if self.crc8check(buf):
                temp = (buf[0] << 8 | buf[1]) & 0xFFFC
                return self.ctemp(temp)
            else:
                return -255

    def read_humidity(self):
        with self._lock:
            self.dev.write(CMD_READ_HUM_NOHOLD)  #measure humidity
            time.sleep(.1)

            data = self.dev.read(3)
            buf = array.array('B', data)

            if self.crc8check(buf):
                humid = (buf[0] << 8 | buf[1]) & 0xFFFC
                return self.chumid(humid)
            else:
                return -255

    def get_value(self, name=None):
        if name == 'Temperature':
            return self.read_temperature()
        elif name == 'Humidity':
            return self.read_humidity()

if __name__ == "__main__":
    obj = HTU21D()
    print "Temp:", round(obj.read_temperature(), 2), "C"
    print "Humid:", round(obj.read_humidity(), 2), "%rH"
