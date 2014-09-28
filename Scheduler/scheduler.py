"""
scheduler for gathering data
"""
from datetime import datetime
import time
from threading import Thread
import urllib2
import json


class Scheduler():
    interval = None
    _stop_request = None
    _tread = None
    _tasks = []

    def __init__(self, interval):
        self.interval = interval

    def start(self, join=False):
        self._stop_request = False
        self._tread = Thread(target=self.work)
        self._tread.start()
        if join:
            self._tread.join()

    def stop(self):
        self._stop_request = True
        self._tread.join()

    def work(self):
        while not self._stop_request:
            print datetime.now()
            for task in self._tasks:
                task()
            time.sleep(self.interval)

    def add_task(self, task, *args):
        if callable(task):
            self._tasks.append(task)


def test():
    print "test"

if __name__ == "__main__":
        scheduler = Scheduler(1)
        scheduler.start()

        time.sleep(5)
        scheduler.add_task(test)

        time.sleep(5)
        scheduler.stop()

        #response = urllib2.urlopen("http://127.0.0.1:5000/api/point/temperature1").read()
        #response_dict = json.loads(response)
        #print response