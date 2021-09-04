import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
from pathlib import Path
import os
import pandas as pd
import threading
from machine_learning.neural_framework import Neural_Framework

'''
Unsupervised Model that will group Normalized stock data in different ways
'''

class Pattern_Net(Neural_Framework):
    def __init__(self,epochs,batch_size):
        super().__init__(epochs, batch_size)
    def create_model(self,model_choice=None):
        pass
    def run_model(self):
        pass
    def save_model(self):
        pass
    def load_model(self,name=None):
        pass