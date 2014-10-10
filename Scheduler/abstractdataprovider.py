from abc import ABCMeta, abstractmethod

class AbstractDataProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_value(self, name=None):
        pass