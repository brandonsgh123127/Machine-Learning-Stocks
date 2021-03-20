import keras 
import tensorflow as tf
import numpy as np
import pandas
from matplotlib import pyplot as plt
import yfinance as yf
import datetime
from pandas_datareader import data as pdr

# mmddyyyy to yyyymmdd
# retrieve pandas_datareader object of data
def get_data_from_range(indicator,start_date,end_date):
    formatted_dates = (datetime.datetime.strptime(start_date,"%m%d%Y").strftime("%Y-%m-%d"),datetime.datetime.strptime(end_date,"%m%d%Y").strftime("%Y-%m-%d"))
    return pdr.get_data_yahoo(indicator,start=formatted_dates[0],end=formatted_dates[1])
    
yf.pdr_override()
print(get_data_from_range("AMD", "12212020", "03032021"))