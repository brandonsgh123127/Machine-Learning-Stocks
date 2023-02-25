from abc import ABC, abstractmethod
from pathlib import Path
import os
import random

from keras.models import Model


class Neural_Framework(ABC):
    def __init__(self, epochs, batch_size):
        self.EPOCHS = epochs
        self.BATCHES = batch_size
        self.path = Path(os.getcwd()).absolute()
    @abstractmethod
    def run_model(self, nn: Model):
        pass

    @staticmethod
    def choose_random_ticker(self, csv_file:str):
        with open(csv_file) as f:
            ticker = random.choice(f.readlines())
            ticker = ticker[0:ticker.find(',')]
            print(ticker)
            return ticker

    @abstractmethod
    def run_model(self, nn: Model, rand_date=False):
        pass
