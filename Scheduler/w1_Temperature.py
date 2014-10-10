import os
from abstractdataprovider import AbstractDataProvider


class W1Temperature(AbstractDataProvider):
    w1_base_path = "/sys/bus/w1/devices/"

    def connected_sensors(self):
        return [w1_dir for w1_dir in os.listdir(self.w1_base_path) if w1_dir.startswith("28-00000")]

    def get_value(self, name=None):
        try:
            w1_file_path = self.w1_base_path + name + "/w1_slave"
            w1_file = open(w1_file_path)
            w1_file_text = w1_file.read()
            w1_file.close()

            value_string = w1_file_text.split("\n")[1].split(" ")[9]
            value = float(value_string[2:])
            value /= 1000
        except IOError:
            print "IOError - return default value"
            value = 0.0

        return value

if __name__ == "__main__":
    temperature = W1Temperature()
    sensor_list = temperature.connected_sensors()

    for i in range(0, 10):
        for sensor in sensor_list:
            print sensor + " - %0.2f" % temperature.get_value(sensor)
