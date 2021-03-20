import numpy as np
import pandas
from matplotlib import pyplot as plt
import yfinance as yf
import datetime
from pandas_datareader import data as pdr


class Gather():
    def __init__(self):
        yf.pdr_override()
        self.indicator = ""
        
        
    # mmddyyyy to yyyymmdd
    # retrieve pandas_datareader object of data
    def get_data_from_range(self,indicator,start_date,end_date):
        formatted_dates = (datetime.datetime.strptime(start_date,"%m%d%Y").strftime("%Y-%m-%d"),datetime.datetime.strptime(end_date,"%m%d%Y").strftime("%Y-%m-%d"))
        return pdr.get_data_yahoo(indicator,start=formatted_dates[0],end=formatted_dates[1])
    
    def get_recent_news(self,indica):
    