from scheduler import Scheduler
import urllib, urllib2
from HTU21D import HTU21D
from w1_Temperature import W1Temperature
from abstractdataprovider import AbstractDataProvider


historian_url = "http://127.0.0.1:5000/"


def http_post_value(name, value):
    api_req_url = "%sapi/point_value/%s/%.2f" % (historian_url, name, value)
    print api_req_url
    post_values = urllib.urlencode({'Submit': True})
    response = urllib2.urlopen(api_req_url, post_values)
    response.read()


def post_provider_value(data_provider, sensor_name=None):
    if isinstance(data_provider, AbstractDataProvider):
        value = data_provider.get_value(sensor_name)
        http_post_value(sensor_name, value)
        print "recording %s - %.2f" % (sensor_name, value)

if __name__ == "__main__":
    w1_temps = W1Temperature()
    #w1_sensors = w1_temperature.connected_sensors()
    w1_sensors = ['temperature1']

    scheduler = Scheduler(1)

    for sensor in w1_sensors:
        scheduler.add_task(post_provider_value, w1_temps, sensor)

    scheduler.start(join=True)