import keras 
import tensorflow as tf
import numpy as np
import pandas
from matplotlib import pyplot as plt
import yfinance as yf
from pandas_datareader import data as pdr
yf.pdr_override()
data = pdr.get_data_yahoo("DOW", start="2021-01-01", end="2021-03-15")
print(data.get("Open"))