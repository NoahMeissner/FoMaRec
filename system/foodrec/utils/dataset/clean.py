# Noah Meissner 25.07.2025

from abc import ABC, abstractmethod

class DataClean:

    def __init__(self, raw_data):
        self.raw_data = raw_data

    @abstractmethod
    def preprocess_data(self):
        return self.raw_data