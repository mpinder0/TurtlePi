from scheduler import Scheduler
from HTU21D import HTU21D
from w1_Temperature import W1Temperature
import signal
import sys


def signal_handler(signal, frame):
    print "Exiting..."
    scheduler.stop()
    sys.exit(0)

historian_url = "http://192.168.0.16:5000/"

w1_temps = W1Temperature()
humidity = HTU21D()
w1_sensors = w1_temps.connected_sensors()

scheduler = Scheduler(historian_url)
interval = 5

for sensor in w1_sensors:
    scheduler.add_sensor(interval, w1_temps, sensor, sensor)

scheduler.add_sensor(interval, humidity, "Temperature", "HTU21D_Temp")
scheduler.add_sensor(interval, humidity, "Humidity", "HTU21D_Hum")

signal.signal(signal.SIGINT, signal_handler)
scheduler.start()

app_exit = False
while not app_exit:
    in_string = raw_input("Command (Q to exit):")
    if in_string == "Q":
        scheduler.stop()
        app_exit = True