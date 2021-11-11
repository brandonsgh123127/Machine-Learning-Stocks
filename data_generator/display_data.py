import matplotlib.pyplot as plt
import pandas as pd
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
from pathlib import Path
import os
import gc
import numpy as np
import threading

'''
Easily display unfiltered data given the ticker and date range specified on the file
Class implements matplotlib and pandas
'''
class Display():
    def __init__(self):
        # print("Display instance initialized!")
        self.data_display = pd.DataFrame()
        self.study_display = pd.DataFrame()
        self.listLock = threading.Lock()
        self.keltner_display = pd.DataFrame()
        self.fig, self.axes = plt.subplots(2, 2) # plot 4 max
        self.fig.set_size_inches(10.5, 10.5)
        self.fib_display = pd.DataFrame()
        self.path = Path(os.getcwd()).parent.absolute() 
        self.color_map = {'blue':'b',
                        'green':'g',
                        'red':'r',
                        'cyan':'c',
                        'magenta':'m',
                        'yellow':'y',
                        'black':'k',
                        'white':'w'}
    def read_studies_data(self,predicted=None,actual=None,keltner=None,fib=None):
        self.data_display = actual
        self.data_predict_display = predicted
        if keltner is not None and fib is not None:
            self.keltner_display=keltner
            self.fib_display = fib
        pd.set_option("display.max.columns", None)
    def display_box(self,data=None,row=0,col=0,has_actuals=False):

        c = 'blue'
        if data is None:
            raise Exception('[ERROR] data cannot be None!  Exiting display boxplot...')
        try:
            self.fib_display = self.fib_display.reset_index().set_axis(['index','0.202','0.236','0.241','0.273','0.283','0.316','0.382','0.5','0.618','0.796','1.556','3.43','3.83','5.44'], 1)
        except:
            self.fib_display = self.fib_display.set_axis(['index','0.202','0.236','0.241','0.273','0.283','0.316','0.382','0.5','0.618','0.796','1.556','3.43','3.83','5.44'], 1)
        # self.fib_display = self.fib_display.loc[self.fib_display.index.repeat(len(self.keltner_display.index) + 2)]
        self.fib_display = self.fib_display.reset_index().astype('float')
        try:
            self.fib_display = self.fib_display.drop(['level_0'],axis=1)
        except:
            pass
        self.fib_display['0.202'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col],color='green',x='0.202',y='0.202')
        self.fib_display['0.236'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['0.241'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['0.273'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['0.283'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['0.316'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['0.382'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['0.5'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['0.618'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['0.796'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['1.556'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['3.43'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['3.83'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        self.fib_display['5.44'].transpose().iloc[int(len(data.index)/1.33+1):].plot.line(ax=self.axes[row,col])
        if has_actuals:
            data = data.astype('float')
            data.iloc[int(len(data.index)/1.33+1):-1].transpose().boxplot(ax=self.axes[row,col],patch_artist=True,
                                              boxprops=dict(facecolor=(0.1,0.5,0.4,0.5)),
                                                    capprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(data.iloc[-2]['Close']) else 'green' ),
                                                    showfliers=False,
                                                    showcaps=False,
                                                    flierprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(data.iloc[-2]['Close']) else 'green',
                                                    markeredgecolor='red' if float(data.iloc[-1]['Close']) < float(data.iloc[-2]['Close']) else 'green'),
                                                    medianprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(data.iloc[-2]['Close']) else 'green'),
                                                    autorange=True)
        else:
            data = data.astype('float')
            data.iloc[int(len(data.index)/1.33+1):].transpose().boxplot(ax=self.axes[row,col],patch_artist=True,
                                              boxprops=dict(facecolor=(0.1,0.5,0.4,0.5)),
                                                    capprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(data.iloc[-2]['Close']) else 'green' ),
                                                    showfliers=False,
                                                    showcaps=False,
                                                    flierprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(data.iloc[-2]['Close']) else 'green',
                                                    markeredgecolor='red' if float(data.iloc[-1]['Close']) < float(data.iloc[-2]['Close']) else 'green'),
                                                    medianprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(data.iloc[-2]['Close']) else 'green'),
                                                    autorange=True)
        self.keltner_display = self.keltner_display.reset_index().iloc[int(len(self.keltner_display.index)/1.33+1):].reset_index().astype('float')
        self.keltner_display['middle'].transpose().plot.line(ax=self.axes[row,col])
        self.keltner_display['upper'].transpose().plot.line(ax=self.axes[row,col])
        self.keltner_display['lower'].transpose().plot.line(ax=self.axes[row,col])
        # self.fib_display.reindex_like(self.data_display).transpose().plot(ax=self.axes[0,0]).line()

    def display_divergence(self,color=None,has_actuals=False,row=1,col=1):
        data = self.data_predict_display.reset_index()
        data.transpose().plot(ax=self.axes[row,col],kind='line',color=color)
    def display_line(self,color='g',row=0,col=1):
        indices_dict = {0:'Open',1:'Close',2:'Range'}
        self.data_display2 = pd.concat([self.data_display.reset_index(),self.data_predict_display.reset_index()],ignore_index=False).set_flags(allows_duplicate_labels=True)
        self.data_display2['index'] = [0,0]
        self.data_display2 = self.data_display2.set_index('index')
        self.data_display2['Open'].plot(ax=self.axes[row,col],x='index',y='Open',style=f'{self.color_map.get(color)}x')
        self.data_display2['index'] = [1,1]
        self.data_display2 = self.data_display2.set_index('index')
        self.data_display2['Close'].plot(ax=self.axes[row,col],x='index',y='Close',style=f'{self.color_map.get(color)}o')
        self.data_display2['index'] = [2,2]
        self.data_display2 = self.data_display2.set_index('index')
        self.data_display2['Range'].plot(x='index',y='Range',style='mo', ax=self.axes[row,col])
        self.data_display2['index'] = [3,3]

        for i,row2 in enumerate(self.data_display2.index):
            for j,col2 in enumerate(self.data_display2.columns):
                if i == 0:
                    y = round(self.data_display2.iloc[i][j],2)
                    self.axes[row,col].text(j, y, f'{indices_dict.get(j)} - A {y}',size='x-small')
                else:
                    y = round(self.data_display2.iloc[i][j],2)
                    self.axes[row,col].text(j, y, f'{indices_dict.get(j)} - P {y}',size='x-small')
    def display_predict_only(self,color=None,row=0,col=1):
        indices_dict = {0:'Open',1:'Close',2:'Range'}
        self.data_predict_display2 = self.data_predict_display
        self.data_predict_display2['index'] = [0]
        self.data_predict_display2 = self.data_predict_display2.set_index('index')
        self.data_predict_display2['Open'].plot(ax=self.axes[row,col],x='index',y='Open',style=f'{self.color_map.get(color)}x')
        self.data_predict_display2['index'] = [1]
        self.data_predict_display2 = self.data_predict_display2.set_index('index')
        self.data_predict_display2['Close'].plot(ax=self.axes[row,col],x='index',y='Close',style=f'{self.color_map.get(color)}o')
        self.data_predict_display2['index'] = [2]
        data = self.data_predict_display2.set_index('index')
        data['Range'].plot(x='index',y='Range',style='mo', ax=self.axes[row,col])
        data['index'] = [3]

        for i,row2 in enumerate(self.data_predict_display2.index):
            for j,col2 in enumerate(self.data_predict_display2.columns):
                y = round(data.iloc[i][j],2)
                self.axes[row,col].text(j, y, f'{indices_dict.get(j)} - P {y}',size='x-small')

# dis = Display()
# dis.read_studies("2021-06-22--2021-08-12","SPY")
# dis.display_divergence(ticker='SPY', dates=None, color='green')
# locs, labels = plt.xticks()
# dis.display_box()
# # plt.xticks(locs)
# plt.show()