import queue

import matplotlib.pyplot as plt
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
        self.fig, self.axes = plt.subplots(2, 2)
        self.fig.set_size_inches(10.5, 10.5)
        self.fib_display = pd.DataFrame()
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

    def display_box(self, data=None, row=0, col=0, has_actuals=False,without_fib=False, only_fib=False,opt_fib_vals=[]):
        c = 'blue'
        if data is None:
            raise Exception('[ERROR] data cannot be None!  Exiting display boxplot...')

        try:
            data_len = len(data.index)
            if has_actuals:
                if not only_fib:
                    data = data.iloc[int(data_len / 1.33 + 1):-1].reset_index().astype(np.float_)
                else:
                    data = data.iloc[:-1].reset_index().astype(np.float_)
                if not without_fib and not only_fib:
                    fib_display = self.fib_display.reset_index()
                    if len(fib_display.index) < data_len:
                        fib_display = fib_display.loc[fib_display.index.repeat(data_len - len(fib_display.index) + 4)]
                    fib_display = fib_display.iloc[int(data_len / 1.33 + 1):].reset_index().astype(np.float_)
                    self.studies = self.studies.iloc[int(data_len / 1.33 + 1):].reset_index().astype(np.float_)
            else:
                if not only_fib:
                    data = data.iloc[int(data_len / 1.33 + 1):]
                if not without_fib and not only_fib:
                    fib_display = self.fib_display.reset_index()
                    if len(fib_display.index) > data_len:
                        fib_display = fib_display.iloc[-data_len:]
                    self.studies = self.studies.iloc[int(data_len / 1.33 + 1):].reset_index().astype(np.float_)
            # if only_fib, expand the data so it covers the length of the elongated data
            if only_fib:
                fib_display = self.fib_display.loc[
                    self.fib_display.index.repeat(int(data_len/len(self.fib_display))+1)]
                fib_display = self.fib_display.reset_index().astype(np.float_)
            data = data.reset_index().drop(columns=['index']).astype(np.float_)
        except:
            pass
        try:
            data = data.drop(columns=['level_0']).astype(np.float_)
        except:
            pass
        try:
            fib_display = fib_display.drop(columns=['level_0'])
        except:
            pass
        try:
            self.studies = self.studies.drop(columns=['level_0'])
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
                if abs(1 - (fib_display['0.202'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2.33:
                    fib_display['0.202'].transpose().plot.line(ax=self.axes[row, col], color='green', x='0.202', y='0.202')
                if abs(1 - (fib_display['0.236'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2.33:
                    fib_display['0.236'].transpose().plot.line(ax=self.axes[row, col], color='blue')
                if abs(1 - (fib_display['0.241'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2.33:
                    fib_display['0.241'].transpose().plot.line(ax=self.axes[row, col], color='blue')
                if abs(1 - (fib_display['0.273'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2.33:
                    fib_display['0.273'].transpose().plot.line(ax=self.axes[row, col], color='brown')
                if abs(1 - (fib_display['0.283'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2.33:
                    fib_display['0.283'].transpose().plot.line(ax=self.axes[row, col], color='orange')
                if abs(1 - (fib_display['0.316'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2.12:
                    fib_display['0.316'].transpose().plot.line(ax=self.axes[row, col], color='orange')
                if abs(1 - (fib_display['0.382'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2.12:
                    fib_display['0.382'].transpose().plot.line(ax=self.axes[row, col], color='red')
                if abs(1 - (fib_display['0.5'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2:
                    fib_display['0.5'].transpose().plot.line(ax=self.axes[row, col], color='blue')
                if abs(1 - (fib_display['0.523'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2:
                    fib_display['0.523'].transpose().plot.line(ax=self.axes[row, col], color='blue',linestyle='dashed')
                if abs(1 - (fib_display['0.618'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2:
                    fib_display['0.618'].transpose().plot.line(ax=self.axes[row, col], color='purple')
                if abs(1 - (fib_display['0.796'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2:
                    fib_display['0.796'].transpose().plot.line(ax=self.axes[row, col], color='brown')
                if abs(1 - (fib_display['0.923'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2:
                    fib_display['0.923'].transpose().plot.line(ax=self.axes[row, col], color='brown',linestyle='dashdot')
                if abs(1 - (fib_display['1.556'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target/2:
                    fib_display['1.556'].transpose().plot.line(ax=self.axes[row, col], color='orange',linestyle='dotted')
                if abs(1 - (fib_display['2.17'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target:
                    fib_display['2.17'].transpose().plot.line(ax=self.axes[row, col], color='black',linestyle='dashdot')
                if abs(1 - (fib_display['2.493'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target:
                    fib_display['2.493'].transpose().plot.line(ax=self.axes[row, col], color='brown')
                if abs(1 - (fib_display['2.86'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target:
                    fib_display['2.86'].transpose().plot.line(ax=self.axes[row, col], color='blue')
                if abs(1 - (fib_display['3.43'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target:
                    fib_display['3.43'].transpose().plot.line(ax=self.axes[row, col], color='black',linestyle='dotted')
                if abs(1 - (fib_display['3.83'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target:
                    fib_display['3.83'].transpose().plot.line(ax=self.axes[row, col], color='brown')
                if abs(1 - (fib_display['4.32'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target:
                    fib_display['4.32'].transpose().plot.line(ax=self.axes[row, col], color='pink')
                if abs(1 - (fib_display['5.01'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target:
                    fib_display['5.01'].transpose().plot.line(ax=self.axes[row, col], color='red',linestyle='dashed')
                if abs(1 - (fib_display['5.63'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target:
                    fib_display['5.63'].transpose().plot.line(ax=self.axes[row, col], color='blue')
                if abs(1 - (fib_display['5.96'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target:
                    fib_display['5.96'].transpose().plot.line(ax=self.axes[row, col], color='brown',linestyle='dotted')
                if abs(1 - (fib_display['7.17'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target * (1.2):
                    fib_display['7.17'].transpose().plot.line(ax=self.axes[row, col], color='pink')
                if abs(1 - (fib_display['8.23'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target * (1.2):
                    fib_display['8.23'].transpose().plot.line(ax=self.axes[row, col], color='orange')
                if abs(1 - (fib_display['9.33'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target * (1.25):
                    fib_display['9.33'].transpose().plot.line(ax=self.axes[row, col], color='black')
                if abs(1 - (fib_display['10.13'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target * (1.33):
                    fib_display['10.13'].transpose().plot.line(ax=self.axes[row, col], color='green',linestyle='dashdot')
                if abs(1 - (fib_display['11.13'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target * (1.33):
                    fib_display['11.13'].transpose().plot.line(ax=self.axes[row, col], color='black',linestyle='dashdot')
                if abs(1 - (fib_display['12.54'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target * (1.4):
                    fib_display['12.54'].transpose().plot.line(ax=self.axes[row, col], color='brown',linestyle='dashed')
                if abs(1 - (fib_display['13.17'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target * (1.45):
                    fib_display['13.17'].transpose().plot.line(ax=self.axes[row, col], color='brown',linestyle='dashed')
                if abs(1 - (fib_display['14.17'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target * (1.45):
                    fib_display['14.17'].transpose().plot.line(ax=self.axes[row, col], color='black')
                if abs(1 - (fib_display['15.55'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target * (1.5):
                    fib_display['15.55'].transpose().plot.line(ax=self.axes[row, col], color='green',linestyle='dashed')
                if abs(1 - (fib_display['16.32'].iloc[-1] / data['Close'].iloc[-10:].mean())) < perc_target * (1.5):
                    fib_display['16.32'].transpose().plot.line(ax=self.axes[row, col], color='red',linestyle='dotted')
                fib_display = fib_display.reset_index(drop=True)
            except Exception as e:
                print(f'failed to do fib_display: {e}')
                pass
        if has_actuals:
            bplot = data.transpose().boxplot(ax=self.axes[row, col], patch_artist=True,
                                     boxprops=dict(facecolor='red' if float(data.iloc[-1]['Close']) < float(
                                         data.iloc[-1]['Open']) else 'green'),
                                     capprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(
                                         data.iloc[-1]['Open']) else 'green'),
                                     showfliers=False,
                                     showcaps=False,
                                     flierprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(
                                         data.iloc[-1]['Open']) else 'green',
                                                     markeredgecolor='red' if float(data.iloc[-1]['Close']) < float(
                                                         data.iloc[-2]['Close']) else 'green'),
                                     medianprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(
                                         data.iloc[-1]['Open']) else 'green'),
                                     autorange=True)
        else:
            data = data.astype(np.float_)
            data.transpose().boxplot(ax=self.axes[row, col], patch_artist=True,
                                     boxprops=dict(facecolor='red' if float(data.iloc[-1]['Close']) < float(
                                         data.iloc[-1]['Open']) else 'green'),
                                     capprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(
                                         data.iloc[-1]['Open']) else 'green'),
                                     showfliers=False,
                                     showcaps=False,
                                     flierprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(
                                         data.iloc[-1]['Open']) else 'green',
                                                     markeredgecolor='red' if float(data.iloc[-1]['Close']) < float(
                                                         data.iloc[-1]['Open']) else 'green'),
                                     medianprops=dict(color='red' if float(data.iloc[-1]['Close']) < float(
                                         data.iloc[-1]['Open']) else 'green'),
                                     autorange=True)
            if (row == 0 and col == 0) or (row == 1 and col == 1):
                self.axes[row, col].margins(x=0, y=0)
            color_identifiers = queue.Queue()
            for i,d in data.iterrows():
                color_identifiers.put('red' if float(data.iloc[i]['Close']) < float(
                                             data.iloc[i]['Open']) else 'green')

        if not without_fib and not only_fib:
            self.keltner_display = self.keltner_display.iloc[
                                   int(len(self.keltner_display.index) / 1.33 + 1):].reset_index().astype(np.float_)
        if not only_fib:
            self.keltner_display['middle'].transpose().plot.line(ax=self.axes[row, col])
            self.keltner_display['upper'].transpose().plot.line(ax=self.axes[row, col])
            self.keltner_display['lower'].transpose().plot.line(ax=self.axes[row, col])
            self.keltner_display = self.keltner_display.reset_index(drop=True)
            self.studies['ema14'].reset_index(drop=True).transpose().plot.line(
                ax=self.axes[row, col],color='yellow')
            self.studies['ema30'].reset_index(drop=True).transpose().plot.line(
                ax=self.axes[row, col],color='green')
            self.studies['ema14'] = self.studies['ema14'].reset_index(drop=True)
            self.studies['ema30'] = self.studies['ema30'].reset_index(drop=True)

    def display_divergence(self, color=None, has_actuals=False, row=1, col=1):
        data = self.data_predict_display.reset_index()
        data.transpose().plot(ax=self.axes[row, col], kind='line', color=color)

    def display_line(self, color='g', row=0, col=1, is_divergence=False):
        if is_divergence:
            indices_dict = {0: 'Close'}
        else:
            indices_dict = {0: 'Close EMA14 Distance', 1: 'Close EMA30 Distance',
                            2: 'Close Fib1 Distance',3: 'Close Fib2 Distance',
                            4: 'Num Consec Candle Dir', 5: 'Upper Keltner Close Diff',
                            6: 'Lower Keltner Close Diff', 7: 'Open', 8: 'Close'}
        self.data_display2 = pd.concat([self.data_display.reset_index(), self.data_predict_display.reset_index()],
                                       ignore_index=False).set_flags(allows_duplicate_labels=True)
        self.data_display2['index'] = [0, 0]
        # self.data_display2 = self.data_display2.set_index('index')
        # self.data_display2['Open'].plot(ax=self.axes[row, col], x='index', y='Open',
        #                                 style=f'{self.color_map.get(color)}x')
        #
        # self.data_display2['index'] = [1, 1]
        self.data_display2 = self.data_display2.set_index('index')
        self.axes[row,col].set_xticklabels([])
        self.data_display2['Close'].plot(x='Close', y='Close', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])

        # if divergence, add open label
        try:
            if is_divergence:
                self.data_display2['index'] = [1, 1]
                self.data_display2 = self.data_display2.set_index('index')
                self.data_display2['Open'].plot(x='index', y='Open', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
        except Exception as e:
            raise Exception(
                f'[INFO] Failed to draw "Range" column!\n{len(self.data_predict_display2.columns)}\n{self.data_predict_display2.columns}\n{str(e)}')
        for i, row2 in enumerate(self.data_display2.index):
            for j, col2 in enumerate(self.data_display2.columns):
                if not is_divergence:
                    if i == 0:
                        if j == 8:  # Bottom Left
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - A {y}', size='x-small')
                    else:
                        if j == 8:  # Top right
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - P {y}', size='x-small')
                else:  # divergence
                    if i == 0:
                        if j == 0 or j == 1 or j == 2:
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - A {y}', size='x-small')
                    else:
                        if j == 0 or j == 1 or j == 2:
                            y = round(self.data_display2.iloc[i][j], 2)
                            self.axes[row, col].text(i, y, f'{indices_dict.get(j)} - P {y}', size='x-small')

    def display_predict_only(self, color=None, row=0, col=1, is_divergence=False):
        if is_divergence:
            indices_dict = {0: 'Close'}
        else:
            indices_dict = {0: 'Close EMA14 Distance', 1: 'Close EMA30 Distance',
                            2: 'Close Fib1 Distance',3: 'Close Fib2 Distance',
                            4: 'Num Consec Candle Dir', 5: 'Upper Keltner Close Diff',
                            6: 'Lower Keltner Close Diff', 7: 'Open', 8: 'Close'}

        self.data_predict_display2 = self.data_predict_display
        self.data_predict_display2['index'] = [0]
        # self.data_predict_display2 = self.data_predict_display2.set_index('index')
        # self.data_predict_display2['Open'].plot(ax=self.axes[row, col], x='index', y='Open',
        #                                         style=f'{self.color_map.get(color)}x')
        #
        # self.data_predict_display2['index'] = [1]
        data = self.data_predict_display2.set_index('index')
        self.axes[row,col].set_xticklabels([])
        data['Close'].plot(x='index', y='Close', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
        # Under divergence print range label
        try:
            if is_divergence:
                self.data_predict_display2['index'] = [2]
                data = self.data_predict_display2.set_index('index')
                data['Open'].plot(x='index', y='Open', style=f'{self.color_map.get(color)}o', ax=self.axes[row, col])
                data['index'] = [3]
        except Exception as e:
            raise Exception(
                f'[INFO] Failed to draw "Open" column!\n{len(self.data_predict_display2.columns)}\n{self.data_predict_display2.columns}\n{str(e)}')

        for i, row2 in enumerate(self.data_predict_display2.index):
            for j, col2 in enumerate(self.data_predict_display2.columns):
                if is_divergence:
                    if j == 0 or j == 1 or j == 2:
                        y = round(data.iloc[i][j], 2)
                        self.axes[row, col].text(j, y, f'{indices_dict.get(j)} - P {y}', size='x-small')
                else:
                    if j == 7 or j == 8:
                        y = round(data.iloc[i][j], 2)
                        self.axes[row, col].text(j, y, f'{indices_dict.get(j)} - P {y}', size='x-small')
# dis = Display()
# dis.read_studies("2021-06-22--2021-08-12","SPY")
# dis.display_divergence(ticker='SPY', dates=None, color='green')
# locs, labels = plt.xticks()
# dis.display_box()
# # plt.xticks(locs)
# plt.show()
