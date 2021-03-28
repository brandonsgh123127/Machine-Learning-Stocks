import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
from pathlib import Path
import os

class Display():
    def __init__(self):
        print("Display instance initialized!")
        self.data_display = pd.DataFrame()
        self.study_display = pd.DataFrame()
        self.path = Path(os.getcwd()).parent.absolute() 
    def read_studies(self,date,ticker):
        self.data_display = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_data.csv').drop(['Adj Close'],axis=1)
        self.study_display = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_studies.csv',index_col=0)
        pd.set_option("display.max.columns", None)
    def display_box(self):
        self.data_display.transpose().boxplot()
        #self.data_display.plot.box()
    def display_line(self):
        self.study_display['index'] = range(1, len(self.study_display) + 1)
        self.study_display.reset_index().plot(x='index')
dis = Display()
dis.read_studies("2018-01-13--2018-03-31","SHOP")
dis.display_line()
locs, labels = plt.xticks()
dis.display_box()
plt.xticks(locs)
plt.show()