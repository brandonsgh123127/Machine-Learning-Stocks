import queue

import matplotlib.pyplot as plt
from matplotlib import use
import numpy as np
import pandas as pd
from pathlib import Path
import os
import threading

'''
Easily display unfiltered data given the ticker and date range specified on the file
Class implements matplotlib and pandas
'''


class Display:
    def __init__(self):
        self.studies = None
        self.data_predict_display = None
        self.data_display = pd.DataFrame()
        self.study_display = pd.DataFrame()
        self.listLock = threading.Lock()
        self.keltner_display = pd.DataFrame()
        use('agg')
        self.fig, self.axes = plt.subplots(2, 2)
        self.pixel_width = 960
        self.pixel_height = 540
        self.req_dpi = 50
        self.fig.set_size_inches(self.pixel_width / float(self.req_dpi),
                               self.pixel_height / float(self.req_dpi))
        self.path = Path(os.getcwd()).absolute()
        self.color_map = {'blue': 'b',
                          'green': 'g',
                          'red': 'r',
                          'cyan': 'c',
                          'magenta': 'm',
                          'yellow': 'y',
                          'black': 'k',
                          'white': 'w'}
    def read_studies_data(self, predicted=None, actual=None, keltner=None, fib=None, studies=None):
        self.data_display = actual
        self.data_predict_display = predicted
        self.keltner_display = keltner
        self.fib_display = fib
        self.studies = studies
        pd.set_option("display.max.columns", None)
    def clear_subplots(self):
        plt.clf()
        self.fig, self.axes = plt.subplots(2, 2)

    def display_box(self, data=None, row=0, col=0, has_actuals=False,without_fib: bool =False, only_fib: bool=False,opt_fib_vals=[]):
        self.axes[row,col].clear()
        self.fig.set_size_inches(self.pixel_width / float(self.req_dpi),
                               self.pixel_height / float(self.req_dpi))
        c = 'blue'
        if data is None:
            raise Exception('[ERROR] data cannot be None!  Exiting display boxplot...')
        try:
            try:
                self.studies = self.studies.drop(columns=['index'])
            except:
                pass
            try:
                self.studies = self.studies.drop(columns=['level_0'])
            except:
                pass
            try:
                self.keltner_display = self.keltner_display.drop(columns=['level_0'])
            except:
                pass
            try:
                self.fib_display = self.fib_display.drop(columns=['level_0'])
            except:
                pass

            try:
                data = data.drop(columns=['level_0'])
            except:
                pass
            data_len = len(data.index)
            studies = self.studies.copy()
            keltner_display = self.keltner_display.copy()
            fib_display = self.fib_display
            if not without_fib and not only_fib: # Normal - when fib/studies are active
                data = data.iloc[-int(data_len / 1.66):].reset_index().astype(np.float_)
                data_len = len(data.index)
                fib_display = fib_display.iloc[-data_len:].reset_index()
                studies = studies.iloc[-data_len:].reset_index().astype(np.float_)
                keltner_display = keltner_display.iloc[-data_len:].reset_index().astype(np.float_)
            elif not only_fib: # When only studies,no fib
                data = data.iloc[-8:].reset_index().astype(np.float_)
                data_len = len(data.index)
                fib_display = fib_display.iloc[-data_len:].reset_index()
                studies = studies.iloc[-data_len:].reset_index().astype(np.float_)
                keltner_display = keltner_display.iloc[-data_len:].reset_index().astype(np.float_)
            elif only_fib:
                fib_display = self.fib_display.loc[
                    self.fib_display.index.repeat(int(data_len/len(self.fib_display['0.202']))+1)]
                fib_display = self.fib_display.reset_index().astype(np.float_)
            data = data.reset_index().drop(columns=['index']).astype(np.float_)
        except Exception as e:
            print(f"[INFO] Failed to reduce size of data for display.\nException: {e}")
        try:
            fib_display = fib_display.drop(columns=['level_0'])
        except:
            pass
        try:
            studies = studies.drop(columns=['level_0'])
        except:
            pass
        if not without_fib:
            try:
                orig_labels = ['index', '0.202', '0.236', '0.241', '0.273', '0.283', '0.316', '0.382', '0.5', '0.523', '0.618', '0.796',
                         '0.923', '1.556', '2.17', '2.493', '2.86', '3.43',
                         '3.83', '4.32', '5.01', '5.63', '5.96',
                        '7.17', '8.23','9.33','10.13','11.13', '12.54',
                        '13.17', '14.17', '15.55', '16.32']
                for val in opt_fib_vals:
                    orig_labels.append(val)
                try:
                    fib_display = fib_display.set_axis(
                        labels=orig_labels, axis=1)
                except:
                    fib_display = fib_display.set_axis(
                        labels=orig_labels, axis=1)
                perc_target = 0.08
                for fib_val in opt_fib_vals:
                    fib_display[f'{fib_val}'].transpose().plot.line(ax=self.axes[row, col], color='purple',linestyle='dashed')
                # fib_display = fib_display.loc[fib_display.index.repeat(len(self.keltner_display.index) + 2)]
                if abs(1 - (fib_display['0.202'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.202'].transpose().plot.line(ax=self.axes[row, col], color='green', x='0.202', y='0.202')
                if abs(1 - (fib_display['0.236'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.236'].transpose().plot.line(ax=self.axes[row, col], color='blue')
                if abs(1 - (fib_display['0.241'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.241'].transpose().plot.line(ax=self.axes[row, col], color='blue')
                if abs(1 - (fib_display['0.273'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.273'].transpose().plot.line(ax=self.axes[row, col], color='brown')
                if abs(1 - (fib_display['0.283'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.283'].transpose().plot.line(ax=self.axes[row, col], color='orange')
                if abs(1 - (fib_display['0.316'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.316'].transpose().plot.line(ax=self.axes[row, col], color='orange')
                if abs(1 - (fib_display['0.382'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.382'].transpose().plot.line(ax=self.axes[row, col], color='red')
                if abs(1 - (fib_display['0.5'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.5'].transpose().plot.line(ax=self.axes[row, col], color='blue')
                if abs(1 - (fib_display['0.523'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.523'].transpose().plot.line(ax=self.axes[row, col], color='blue',linestyle='dashed')
                if abs(1 - (fib_display['0.618'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.618'].transpose().plot.line(ax=self.axes[row, col], color='purple')
                if abs(1 - (fib_display['0.796'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.796'].transpose().plot.line(ax=self.axes[row, col], color='brown')
                if abs(1 - (fib_display['0.923'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['0.923'].transpose().plot.line(ax=self.axes[row, col], color='brown',linestyle='dashdot')
                if abs(1 - (fib_display['1.556'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['1.556'].transpose().plot.line(ax=self.axes[row, col], color='orange',linestyle='dotted')
                if abs(1 - (fib_display['2.17'].iloc[-1] / data['Close'].iloc[-4:].mean())) <  perc_target or (row == 2 and col == 2):
                    fib_display['2.17'].transpose().plot.line(ax=self.axes[row, col], color='black',linestyle='dashdot')
                if abs(1 - (fib_display['2.493'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['2.493'].transpose().plot.line(ax=self.axes[row, col], color='brown')
                if abs(1 - (fib_display['2.86'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['2.86'].transpose().plot.line(ax=self.axes[row, col], color='blue')
                if abs(1 - (fib_display['3.43'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['3.43'].transpose().plot.line(ax=self.axes[row, col], color='black',linestyle='dotted')
                if abs(1 - (fib_display['3.83'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['3.83'].transpose().plot.line(ax=self.axes[row, col], color='brown')
                if abs(1 - (fib_display['4.32'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['4.32'].transpose().plot.line(ax=self.axes[row, col], color='pink')
                if abs(1 - (fib_display['5.01'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['5.01'].transpose().plot.line(ax=self.axes[row, col], color='red',linestyle='dashed')
                if abs(1 - (fib_display['5.63'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['5.63'].transpose().plot.line(ax=self.axes[row, col], color='blue')
                if abs(1 - (fib_display['5.96'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['5.96'].transpose().plot.line(ax=self.axes[row, col], color='brown',linestyle='dotted')
                if abs(1 - (fib_display['7.17'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['7.17'].transpose().plot.line(ax=self.axes[row, col], color='pink')
                if abs(1 - (fib_display['8.23'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['8.23'].transpose().plot.line(ax=self.axes[row, col], color='orange')
                if abs(1 - (fib_display['9.33'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['9.33'].transpose().plot.line(ax=self.axes[row, col], color='black')
                if abs(1 - (fib_display['10.13'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['10.13'].transpose().plot.line(ax=self.axes[row, col], color='green',linestyle='dashdot')
                if abs(1 - (fib_display['11.13'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['11.13'].transpose().plot.line(ax=self.axes[row, col], color='black',linestyle='dashdot')
                if abs(1 - (fib_display['12.54'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['12.54'].transpose().plot.line(ax=self.axes[row, col], color='brown',linestyle='dashed')
                if abs(1 - (fib_display['13.17'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['13.17'].transpose().plot.line(ax=self.axes[row, col], color='brown',linestyle='dashed')
                if abs(1 - (fib_display['14.17'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['14.17'].transpose().plot.line(ax=self.axes[row, col], color='black')
                if abs(1 - (fib_display['15.55'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['15.55'].transpose().plot.line(ax=self.axes[row, col], color='green',linestyle='dashed')
                if abs(1 - (fib_display['16.32'].iloc[-1] / data['Close'].iloc[-4:].mean())) < perc_target or (row == 2 and col == 2):
                    fib_display['16.32'].transpose().plot.line(ax=self.axes[row, col], color='red',linestyle='dotted')
                fib_display = fib_display.reset_index(drop=True)
            except Exception as e:
                print(f'failed to do fib_display: {e}')
                pass
        up = data[data.Close >= data.Open]
        down = data[data.Close < data.Open]
        col1 = 'green'
        col2 = 'red'
        width = .4
        width2 = .05
        plt.sca(self.axes[row, col])
        plt.bar(up.index, up.Close - up.Open, width, bottom=up.Open, color=col1)
        plt.bar(up.index, up.High - up.Close, width2, bottom=up.Close, color=col1)
        plt.bar(up.index, up.Low - up.Open, width2, bottom=up.Open, color=col1)
        plt.bar(down.index, down.Close - down.Open, width, bottom=down.Open, color=col2)
        plt.bar(down.index, down.High - down.Open, width2, bottom=down.Open, color=col2)
        plt.bar(down.index, down.Low - down.Close, width2, bottom=down.Close, color=col2)
        # if (row == 0 and col == 0) or (row == 2 and col == 2):
        #     self.axes[row, col].margins(x=0, y=0)
        # color_identifiers = queue.Queue()
        # for i,d in data.iterrows():
        #     color_identifiers.put('red' if float(data.iloc[i]['Close']) < float(
        #                                  data.iloc[i]['Open']) else 'green')

        # if not without_fib and not only_fib:
        #     keltner_display = keltner_display.iloc[-len(data.index)-1:].reset_index().astype(np.float_)
        if not only_fib:
            # keltner_display = keltner_display.reset_index()
            keltner_display['middle'].transpose().plot.line(ax=self.axes[row, col],color='green')
            keltner_display['upper'].transpose().plot.line(ax=self.axes[row, col],color='purple')
            keltner_display['lower'].transpose().plot.line(ax=self.axes[row, col],color='red')
            # keltner_display = keltner_display.reset_index(drop=True)
            studies['ema14'].reset_index(drop=True).transpose().plot.line(
                ax=self.axes[row, col],color='blue',linestyle='dashed')
            studies['ema20'].reset_index(drop=True).transpose().plot.line(
                ax=self.axes[row, col],color='green')
            studies['ema30'].reset_index(drop=True).transpose().plot.line(
                ax=self.axes[row, col],color='yellow',linestyle='dashed')
            studies['ema14'] = studies['ema14'].reset_index(drop=True)
            studies['ema30'] = studies['ema30'].reset_index(drop=True)
            # studies['ema20'] = studies['ema20'].iloc[-data_len:].reset_index(drop=True)

    def display_line(self, color='g', row=0, col=1, out = 1):
        self.axes[row,col].clear()
        self.fig.set_size_inches(self.pixel_width / float(self.req_dpi),
                               self.pixel_height / float(self.req_dpi))

        if out == 1:
            indices_dict = {0: 'Close EMA14 Distance', 1: 'Close EMA30 Distance',
                        2: 'Close Fib1 Distance',3: 'Close Fib2 Distance',
                        4: 'Num Consec Candle Dir', 5: 'Upper Keltner Close Diff',
                        6: 'Lower Keltner Close Diff', 7: 'Open', 8: 'Close'}
        elif out == 2:
            indices_dict = {0:'Last2Volume Cur Volume Diff', 1:'Open Upper Kelt Diff',
            2:'Open Lower Kelt Diff', 3:'High Upper Kelt Diff',
            4:'High Lower Kelt Diff', 5:'Low Upper Kelt Diff',
            6:'Low Lower Kelt Diff', 7:'Close Upper Kelt Diff',
            8:'Close Lower Kelt Diff', 9:'EMA 14 30 Diff',
            10:'Base Fib High Diff', 11:'Base Fib Low Diff',
            12:'Next1 Fib High Diff', 13:'Next1 Fib Low Diff',
            14:'Next2 Fib High Diff', 15:'Next2 Fib Low Diff',
            16:'Open', 17:'High', 18:'Low', 19:'Close',
            20:'Last3High Base Fib', 21:'Last3Low Base Fib',
            22:'Last3High Next1 Fib', 23:'Last3Low Next1 Fib',
            24:'Last3High Next2 Fib', 25:'Last3Low Next2 Fib'}
        elif out == 3:
            indices_dict = {0:'Upper Kelt',
            1: 'Lower Kelt', 2:'Middle Kelt', 3:'EMA 14', 4:'EMA 30',
            5:'Open', 6:'High', 7:'Low', 8:'Close',
            9:'Last3High', 10:'Last3Low'}
        elif out == 4:
            indices_dict = {0: 'Upper Kelt',
                            1: 'Lower Kelt', 2: 'Middle Kelt', 3: 'EMA 14', 4: 'EMA 30',
                            5: 'Open', 6: 'High', 7: 'Low', 8: 'Close', 9: 'Base Fib',
                            10: 'Next1 Fib', 11: 'Next2 Fib',
                            12: 'Last3High', 13: 'Last3Low'}

        self.data_display2 = pd.concat([self.data_display.reset_index(), self.data_predict_display.reset_index()],
                                       ignore_index=False).set_flags(allows_duplicate_labels=True)
        if out == 1:
            self.axes[row,col].set_xticklabels([])
            self.data_display2['Close'].plot(x='Close', y='Close', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
        elif 2 <= out <= 4: # display open,high,low,close
            self.data_display2['index'] = [1,2]
            self.data_display2 = self.data_display2.set_index('index')
            self.axes[row,col].set_xticklabels([])
            self.data_display2['Open'].plot(x='Open', y='Open', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
            self.data_display2['index'] = [1,2]
            self.data_display2 = self.data_display2.set_index('index')
            self.axes[row,col].set_xticklabels([])
            self.data_display2['High'].plot(x='High', y='High', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
            self.data_display2['index'] = [1,2]
            self.data_display2 = self.data_display2.set_index('index')
            self.axes[row,col].set_xticklabels([])
            self.data_display2['Low'].plot(x='Low', y='Low', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
            self.data_display2['index'] = [1,2]
            self.data_display2 = self.data_display2.set_index('index')
            self.axes[row,col].set_xticklabels([])
            self.data_display2['Close'].plot(x='Close', y='Close', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])

        for i, row2 in enumerate(self.data_display2.index):
            for j, col2 in enumerate(self.data_display2.columns):
                if out == 1: #legacy output
                    if i == 0:
                        if j == 8:  # Bottom Left
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - A {y}', size='x-small')
                    else:
                        if j == 8:  # Top right
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - P {y}', size='x-small')
                elif out == 2:
                    if i == 0:
                        if 16 <= j <= 19:  # Bottom Left
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - A {y}', size='x-small')
                    else:
                        if 16 <= j <= 19:  # Top right
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - P {y}', size='x-small')
                elif out == 3:
                    if i == 0:
                        if 5 <= j <= 8:  # Bottom Left
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - A {y}', size='x-small')
                    else:
                        if 5 <= j <= 8:  # Top right
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - P {y}', size='x-small')
                elif out == 4:
                    if i == 0:
                        if 5 <= j <= 8:  # Bottom Left
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - A {y}', size='x-small')
                    else:
                        if 5 <= j <= 8:  # Top right
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - P {y}', size='x-small')

    def display_predict_only(self, color=None, row=0, col=1, out = 2 ):
        self.axes[row,col].clear()
        self.fig.set_size_inches(self.pixel_width / float(self.req_dpi),
                               self.pixel_height / float(self.req_dpi))
        if out == 1:
            indices_dict = {0: 'Close EMA14 Distance', 1: 'Close EMA30 Distance',
                        2: 'Close Fib1 Distance',3: 'Close Fib2 Distance',
                        4: 'Num Consec Candle Dir', 5: 'Upper Keltner Close Diff',
                        6: 'Lower Keltner Close Diff', 7: 'Open', 8: 'Close'}
        elif out == 2:
            indices_dict = {0:'Last2Volume Cur Volume Diff', 1:'Open Upper Kelt Diff',
            2:'Open Lower Kelt Diff', 3:'High Upper Kelt Diff',
            4:'High Lower Kelt Diff', 5:'Low Upper Kelt Diff',
            6:'Low Lower Kelt Diff', 7:'Close Upper Kelt Diff',
            8:'Close Lower Kelt Diff', 9:'EMA 14 30 Diff',
            10:'Base Fib High Diff', 11:'Base Fib Low Diff',
            12:'Next1 Fib High Diff', 13:'Next1 Fib Low Diff',
            14:'Next2 Fib High Diff', 15:'Next2 Fib Low Diff',
            16:'Open', 17:'High', 18:'Low', 19:'Close',
            20:'Last3High Base Fib', 21:'Last3Low Base Fib',
            22:'Last3High Next1 Fib', 23:'Last3Low Next1 Fib',
            24:'Last3High Next2 Fib', 25:'Last3Low Next2 Fib'}
        elif out == 3:
            indices_dict = {0: 'Upper Kelt',
                            1: 'Lower Kelt', 2: 'Middle Kelt', 3: 'EMA 14', 4: 'EMA 30',
                            5: 'Open', 6: 'High', 7: 'Low', 8: 'Close',
                            9: 'Last3High', 10: 'Last3Low'}
        elif out == 4:
            indices_dict = {0: 'Upper Kelt',
                            1: 'Lower Kelt', 2: 'Middle Kelt', 3: 'EMA 14', 4: 'EMA 30',
                            5: 'Open', 6: 'High', 7: 'Low', 8: 'Close', 9: 'Base Fib',
                            10: 'Next1 Fib', 11: 'Next2 Fib',
                            12: 'Last3High', 13: 'Last3Low'}
        self.data_predict_display2 = self.data_predict_display
        if out == 1:
            self.data_predict_display2['index'] = [0]
            data = self.data_predict_display2.set_index('index')
            self.axes[row,col].set_xticklabels([])
            data['Close'].plot(x='index', y='Close', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
        elif 2 <= out <= 4:
            self.data_predict_display2['index'] = [1]
            data = self.data_predict_display2.set_index('index')
            self.axes[row,col].set_xticklabels([])
            data['Open'].plot(x='index', y='Open', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
            self.data_predict_display2['index'] = [1]
            data = self.data_predict_display2.set_index('index')
            self.axes[row,col].set_xticklabels([])
            data['High'].plot(x='index', y='High', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
            self.data_predict_display2['index'] = [1]
            data = self.data_predict_display2.set_index('index')
            self.axes[row,col].set_xticklabels([])
            data['Low'].plot(x='index', y='Low', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
            self.data_predict_display2['index'] = [1]
            data = self.data_predict_display2.set_index('index')
            self.axes[row,col].set_xticklabels([])
            data['Close'].plot(x='index', y='Close', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])

        for i, row2 in enumerate(self.data_predict_display2.index):
            for j, col2 in enumerate(self.data_predict_display2.columns):
                if out == 1:
                    if j == 7 or j == 8:
                        y = round(data.iloc[i][j], 2)
                        self.axes[row, col].text(j, y, f'{indices_dict.get(j)} - P {y}', size='x-small')
                elif out == 2:
                    if 16 <= j <= 19:
                        y = round(data.iloc[i][j], 2)
                        self.axes[row, col].text(j, y, f'{indices_dict.get(j)} - P {y}', size='x-small')
                elif 3 <= out <= 4:
                    if 5 <= j <= 8:
                        y = round(data.iloc[i][j], 2)
                        self.axes[row, col].text(j, y, f'{indices_dict.get(j)} - P {y}', size='x-small')


# dis = Display()
# dis.read_studies("2021-06-22--2021-08-12","SPY")
# locs, labels = plt.xticks()
# dis.display_box()
# # plt.xticks(locs)
# plt.show()
