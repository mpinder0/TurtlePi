"""
scheduler for gathering data
"""
from datetime import datetime
import time
from threading import Thread
from abstractdataprovider import AbstractDataProvider
import requests
from numbers import Number


class Scheduler():
    historian_url = "http://127.0.0.1:5000/"
    _stop_request = None
    _threads = []
    _sensor_data = []

    def __init__(self, historian_url=None):
        if historian_url:
            self.historian_url = historian_url

    def start(self, join=False):
        self._stop_request = False
        for data in self._sensor_data:
            self.start_sensor_task(*data)

    def stop(self):
        self._stop_request = True
        for t in self._threads:
            t.join()
			
    def add_sensor(self, interval, data_provider, sensor_name, point_name):
        if isinstance(data_provider, AbstractDataProvider):
            data = (interval, data_provider, sensor_name, point_name)
            self._sensor_data.append(data)

    def sensor_loop(self, interval, data_provider, sensor_name, point_name):
        while not self._stop_request:
            value = data_provider.get_value(sensor_name)
			if isinstance(value, Number):
				self.http_post_value(point_name, value)
            time.sleep(interval)

    def start_sensor_task(self, interval, data_provider, sensor_name, point_name):
        thread = Thread(target=self.sensor_loop, args=(interval, data_provider, sensor_name, point_name))
        thread.start()
        self._threads.append(thread)

    def http_post_value(self, point_name, value):
        try:
            api_req_url = "%sapi/point_value/%s/%.2f" % (self.historian_url, point_name, value)
            response = requests.post(api_req_url)
            if response.status_code == 201:
                response_dict = response.json()
                has_passed = response_dict["filter_passed"]
                print "%s - %.2f - written: %s" % (point_name, value, has_passed)
            else:
                print "Post failed for \"%s\": return code %s" % (point_name, response.status_code)
        except requests.ConnectionError:
            print "Post failed for \"%s\": ConnectionError" % point_name