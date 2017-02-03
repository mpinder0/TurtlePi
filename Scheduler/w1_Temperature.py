import os
import time
from abstractdataprovider import AbstractDataProvider


class W1Temperature(AbstractDataProvider):
    w1_base_path = "/sys/bus/w1/devices/"

    def connected_sensors(self):
        try:
            return [w1_dir for w1_dir in os.listdir(self.w1_base_path) if w1_dir.startswith("28-00000")]
        except OSError:
            return []

    def get_value(self, name=None):
        try:
            w1_file_path = self.w1_base_path + name + "/w1_slave"
            
			crc_valid = False
			while not crc_valid:
				w1_file = open(w1_file_path)
				w1_file_text = w1_file.read()
				w1_file_lines = w1_file_text.split("\n")
				w1_file.close()
				crc_valid = w1_file_lines[0].find("YES") > 0
				if not crc_valid:
					time.sleep(1)

            value_string = w1_file_lines[1].split(" ")[9]
            value = float(value_string[2:])
            value /= 1000
        except IOError:
            print "Failed to get value for %s - IOError" % name
            value = None

        return value

if __name__ == "__main__":
    temperature = W1Temperature()
    sensor_list = temperature.connected_sensors()

    for i in range(0, 10):
        for sensor in sensor_list:
            print sensor + " - %0.2f" % temperature.get_value(sensor)
