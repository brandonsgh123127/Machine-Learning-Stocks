from abc import abstractmethod
from enum import Enum
import os
from pathlib import Path
from random import random
import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class Unsupervised_Models(Enum):
    KMEANS = 0
    KNN = 1
    FP_GROWTH = 2


class Unsupervised_Framework:
    def __init__(self, algorithm: str):
        self.algorithm =  Unsupervised_Models.KNN and print("[INFO] KNN Initialized!") if algorithm == Unsupervised_Models.KNN.name else \
        self.algorithm =  Unsupervised_Models.KMEANS  and print("[INFO] KMEANS Initialized!") if algorithm == Unsupervised_Models.KMEANS.name else \
        self.algorithm =  Unsupervised_Models.FP_GROWTH  and print("[INFO] FP_GROWTH Initialized!") if algorithm == Unsupervised_Models.FP_GROWTH.name else None
        self.path = Path(os.getcwd()).parent.absolute()
        self.model = None

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def predict(self):
        pass

    def save(self):
        self.model.save(f'{self.path}/data/{self.algorithm}')

    @staticmethod
    def choose_random_ticker(self, csv_file: str):
        with open(csv_file) as f:
            ticker = random.choice(f.readlines())
            ticker = ticker[0:ticker.find(',')]
            print(ticker)
            return ticker

    def load(self, algorithm=None):
        try:
            self.model = keras.models.load_model(
                f'{self.path}/data/{algorithm}')
        except:
            print(f'[INFO] No model exists for {algorithm}...')

    @abstractmethod
    def run(self, rand_date=False):
        pass
