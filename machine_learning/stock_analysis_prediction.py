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
ticker = "dash"
path = Path(os.getcwd()).parent.absolute()

gen = Generator(ticker,path)
gen.studies.set_indicator(f'{ticker}')
dates = (datetime.date.today() - datetime.timedelta(days = 50), datetime.date.today() + datetime.timedelta(days = 0)) #month worth of data
gen.generate_data_with_dates(dates[0],dates[1])
_has_actuals = False
#OK MODEL
data = load(f'{ticker}/{dates[0]}--{dates[1]}_data.csv',has_actuals=_has_actuals,name="model_new_2")
dis = Display()
dis.read_studies_data(data[0],data[1])
locs, labels = plt.xticks()
if _has_actuals:
    dis.display_line(ticker=ticker,dates=dates,color="green")
else:
    dis.display_predict_only(ticker=ticker,dates=dates,color="green")
plt.xticks(locs)
#NEW MODEL
data = load(f'{ticker}/{dates[0]}--{dates[1]}_data.csv',has_actuals=_has_actuals,name="model_new_3")
dis = Display()
dis.read_studies_data(data[0],data[1])
locs, labels = plt.xticks()
dis.display_predict_only(ticker=ticker,dates=dates,color="black")
plt.xticks(locs)
#NEW relu-based model
data = load(f'{ticker}/{dates[0]}--{dates[1]}_data.csv',has_actuals=_has_actuals,name="model_new_4")
dis = Display()
dis.read_studies_data(data[0],data[1])
locs, labels = plt.xticks()
dis.display_predict_only(ticker=ticker,dates=dates,color="magenta")
plt.xticks(locs)


plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict.png')