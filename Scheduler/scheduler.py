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
    _task_args = []

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
            for i, task in enumerate(self._tasks):
                task(*self._task_args[i])
            time.sleep(self.interval)

    def add_task(self, task, *args):
        if callable(task):
            self._tasks.append(task)
            self._task_args.append(args)