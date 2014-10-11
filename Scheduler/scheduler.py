"""
scheduler for gathering data
"""
from datetime import datetime
import time
from threading import Thread


class Scheduler():
    interval = None
    _stop_request = None
    _thread = None
    _tasks = []
    _task_args = []

    def __init__(self, interval):
        self.interval = interval

    def start(self, join=False):
        self._stop_request = False
        self._thread = Thread(target=self.work)
        self._thread.daemon = True
        self._thread.start()
        if join:
            self._thread.join()

    def stop(self):
        self._stop_request = True
        self._thread.join()

    def work(self):
        while not self._stop_request:
            for i, task in enumerate(self._tasks):
                task(*self._task_args[i])
            time.sleep(self.interval)

    def add_task(self, task, *args):
        if callable(task):
            self._tasks.append(task)
            self._task_args.append(args)