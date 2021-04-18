import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt
from machine_learning.neural_network import Network
from machine_learning.neural_network import load
from data_generator.normalize_data import Normalizer
from data_generator._data_generator import Generator
from data_generator.display_data import Display
import datetime


sampler = Sample()
# nn = Network(1,10)
ticker = "MSFT"
path = Path(os.getcwd()).parent.absolute()

gen = Generator(ticker,path)
gen.studies.set_indicator(f'{ticker}')
dates = (datetime.date.today() - datetime.timedelta(days = 23), datetime.date.today())
gen.generate_data(dates[0],dates[1])
# nn.load_model()
data = load(f'{ticker}/{dates[0]}--{dates[1]}_data.csv')

dis = Display()
dis.read_studies(data[0],data[1])
# dis.display_box()
locs, labels = plt.xticks()
dis.display_line()
plt.xticks(locs)
plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict.png')