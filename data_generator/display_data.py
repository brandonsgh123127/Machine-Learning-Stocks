import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
from pathlib import Path
import os

'''
Easily display unfiltered data given the ticker and date range specified on the file
Class implements matplotlib and pandas
'''
class Display():
    def __init__(self):
        print("Display instance initialized!")
        self.data_display = pd.DataFrame()
        self.study_display = pd.DataFrame()
        self.path = Path(os.getcwd()).parent.absolute() 
    def read_studies(self,date,ticker):
        self.data_display = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_data.csv').drop(['Adj Close'],axis=1)
        self.study_display = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_studies.csv',index_col=0)
    def read_studies(self,predicted="",actual=""):
        self.data_display = actual
        self.data_predict_display = predicted
        pd.set_option("display.max.columns", None)
    def display_box(self):
        c = 'blue'
        self.data_display.transpose().boxplot(patch_artist=True,
                                              boxprops=dict(facecolor=(0.1,0.5,0.4,0.5)),
                                                    capprops=dict(color=c),
                                                    whiskerprops=dict(color=c),
                                                    flierprops=dict(color=c, markeredgecolor=c),
                                                    medianprops=dict(color=c)).set_alpha(0.3)
    def display_line(self):
        # indices = ['Open Diff','Close Diff','Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff','Close EMA30 Diff','EMA14 EMA30 Diff']
        # print(self.data_display)
        data = pd.concat([self.data_display.reset_index(),self.data_predict_display.reset_index()],ignore_index=False).set_flags(allows_duplicate_labels=True)
        data_orig = data
        data['index'] = [0,0]
        data = data.set_index('index')
        ax = data['Open Diff'].plot(x='index',y='Open Diff',style='bx',label='Open Diff')
        data['index'] = [1,1]
        data = data.set_index('index')
        ax = data['Close Diff'].plot(x='index',y='Close Diff',style='bo', ax=ax,label='Close Diff')
        data['index'] = [2,2]
        data = data.set_index('index')
        ax = data['Derivative Diff'].plot(x='index',y='Derivative Diff',style='mo', ax=ax,label='Derivative Diff')
        data['index'] = [3,3]
        data = data.set_index('index')
        ax = data['Derivative EMA14'].plot(x='index',y='Derivative Diff',style='co', ax=ax,label='Derivative Diff')
        data['index'] = [4,4]
        data = data.set_index('index')
        ax = data['Derivative EMA30'].plot(x='index',y='Derivative Diff',style='ro', ax=ax,label='Derivative Diff')
        data['index'] = [5,5]
        data = data.set_index('index')
        ax = data['Close EMA14 Diff'].plot(x='index',y='Derivative Diff',style='go', ax=ax,label='Derivative Diff')
        data['index'] = [6,6]
        data = data.set_index('index')
        ax = data['Close EMA30 Diff'].plot(x='index',y='Derivative Diff',style='yo', ax=ax,label='Derivative Diff')
        data['index'] = [7,7]
        data = data.set_index('index')
        ax = data['EMA14 EMA30 Diff'].plot(x='index',y='Derivative Diff',style='bs', ax=ax,label='Derivative Diff')
        # ax2 = self.data_predict_display.plot.scatter(x=indices,y=self.data_predict_display.columns,ax=ax, c='red',label='predicted')
        data['index'] = [0,1]
        data = data.set_index('index')

        print(data)
        for i,row in enumerate(data_orig.index):
            for j,col in enumerate(data_orig.columns):
                if j == 8:
                    continue
                y = round(data.iloc[i][j],2)
                ax.text(j, y, y)
    def display_predict_actual(self):
        c = 'red'
        self.data_predict_display.transpose().boxplot(patch_artist=True,
                                                    boxprops=dict(facecolor=(0.25,0.25,0,0.7)),
                                                    capprops=dict(color=c),
                                                    whiskerprops=dict(color=c),
                                                    flierprops=dict(color=c, markeredgecolor=c),
                                                    medianprops=dict(color=c)).set_alpha(0.7)
        
# dis = Display()
# dis.read_studies("2018-01-13--2018-03-31","SHOP")
# dis.display_line()
# locs, labels = plt.xticks()
# dis.display_box()
# plt.xticks(locs)
# plt.show()