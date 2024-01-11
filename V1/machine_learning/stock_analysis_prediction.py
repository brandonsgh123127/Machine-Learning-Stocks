import cProfile
import inspect
import queue
from asyncio import get_running_loop, gather, new_event_loop
from datetime import datetime, timedelta
from typing import Optional

import keras
from V1.data_generator import Sample
from V1.data_generator._data_generator import Generator
from pathlib import Path
import os

from V1.machine_learning.model import NN_Model
# import matplotlib.pyplot as plt
from V1.machine_learning.neural_network import load, Network
from V1.data_generator.display_data import Display
import threading
import sys
import gc
from V1.threading_impl.Thread_Pool import Thread_Pool
from pandas.tseries.holiday import USFederalHolidayCalendar
from concurrent.futures import ThreadPoolExecutor

class launcher:
    def __init__(self, force_generation: bool = False):
        self._type = None
        self.listLock = threading.Lock()
        self.saved_predictions: queue.Queue = queue.SimpleQueue()
        self.listLock = threading.Lock()
        self._executor = ThreadPoolExecutor(4)
        self.gen = Generator(None, Path(os.getcwd()).absolute(), force_generation)
        self.sampler = Sample(ticker=None,force_generate=force_generation)

    async def display_model(self, nn: NN_Model = None, name: str = "relu_multilayer_l2", _has_actuals: bool = False, ticker: str = "spy",
                      color: str = "blue", force_generation=False, unnormalized_data=False, row=0, col=1,
                      data=None,
                      skip_threshold: float = 0.05,
                      interval: str = '1d',
                      opt_fib_vals: list = [],
                      dis: Optional[Display] = None,skip_display: bool = False,
                      out: int = 1):
        # Call machine learning model
        self.sampler.set_ticker(ticker)
        # self.sampler.reset_data()
        print(f"[INFO] Utilizing `{name}` model to predict data.")
        try:
            ldata = await load(nn,f'{ticker.upper()}', has_actuals=_has_actuals, name=f'{name}',
                         force_generation=force_generation, device_opt='/device:GPU:0', rand_date=False, data=data,
                         interval=interval, sampler=self.sampler,opt_fib_vals=opt_fib_vals)
        except Exception as e:
            print(f"[ERROR] Failed to generate NN data for {ticker.upper()}!\r\nException: {e}")
            raise Exception(e)
        if isinstance(ldata, int): # If None, that means no data was passed into load (ticker is bad now, or failed to generate data)
            return ticker, None, None
        # if skipping display, return only predicted value and last val, as that is what we care about.
        if skip_display:
            print("[INFO] Display portion has been skipped.")
            predict_close = ldata[0]['Close'].iloc[0]
            if isinstance(data, tuple):  # if tuple, take 1st df and get close
                self.saved_predictions.put((ticker, predict_close, data[0]['Close'].iloc[-1]))
                return ticker, predict_close, data[0]['Close'].iloc[-1]
            else:
                self.saved_predictions.put((ticker, predict_close, data['Close'].iloc[-1]))
                return ticker, predict_close, data.iloc[-1]
        # read data for loading into display portion
        with self.listLock:
            print("[INFO] Loading data into display.")
            dis.read_studies_data(ldata[0], ldata[1], ldata[3], ldata[4], ldata[5])
        # display data
        if not _has_actuals:  # if prediction, proceed
            if not unnormalized_data:
                with self.listLock:
                    dis.display_predict_only(color=f'{color}', row=row, col=col,out=out)
            else: # Boxplot
                with self.listLock:
                    dis.display_box(ldata[2].copy(), has_actuals=_has_actuals,without_fib=False,only_fib=False,opt_fib_vals=opt_fib_vals) # Display with fib
                    dis.display_box(ldata[2].copy(), row=1, col=0, has_actuals=_has_actuals, without_fib=True,only_fib=False,opt_fib_vals=opt_fib_vals)#Display without fib
                    dis.display_box(ldata[2].copy(), row=1, col=1, has_actuals=_has_actuals, without_fib=False,only_fib=True,opt_fib_vals=opt_fib_vals)#Display only fib
        else:
            if unnormalized_data:
                with self.listLock:
                    dis.display_box(ldata[2].copy(), has_actuals=_has_actuals,without_fib=False,only_fib=False,opt_fib_vals=opt_fib_vals) # display with fib
                    dis.display_box(ldata[2].copy(), row=1, col=0, has_actuals=_has_actuals, without_fib=True,only_fib=False)#Display without fib
                    dis.display_box(ldata[2].copy(), row=1, col=1, has_actuals=_has_actuals, without_fib=False,only_fib=True)#Display only fib
            else:
                with self.listLock:
                    dis.display_line(color=f'{color}', row=row, col=col, out=out)
        return ticker, ldata[0], ldata[1]



async def main(nn_dict: dict = {}, ticker: str = "SPY",
               has_actuals: bool = True, force_generate=False,
               interval='Daily',opt_fib_vals:list=[],
               dis: Optional[Display] = None,skip_display: bool = False, output: int = 4):
    listLock = threading.Lock()
    launch = launcher(force_generate)
    if ticker is not None:
        ticker = ticker
    else:
        raise ValueError("Failed to find ticker name!")

    # if current trading day, set prediction for tomorrow in date name
    dates = []
    # Confirm end date is valid 
    valid_datetime = datetime.utcnow()
    holidays = USFederalHolidayCalendar().holidays(start=valid_datetime,
                                                   end=(valid_datetime - timedelta(days=7))).to_pydatetime()
    valid_date = valid_datetime.date()
    if (
            datetime.utcnow().hour <= 14 and datetime.utcnow().minute < 30):  # if current time is before 9:30 AM EST, go back a day
        valid_datetime = (valid_datetime - timedelta(days=1))
        valid_date = (valid_date - timedelta(days=1))
    if valid_date.weekday() == 5:  # if saturday
        valid_datetime = (valid_datetime - timedelta(days=1))
        valid_date = (valid_date - timedelta(days=1))
    if valid_date.weekday() == 6:  # if sunday
        valid_datetime = (valid_datetime - timedelta(days=2))
        valid_date = (valid_date - timedelta(days=2))
    if valid_date in holidays and 0 <= valid_date.weekday() <= 4:  # week day holiday
        valid_datetime = (valid_datetime - timedelta(days=1))
        valid_date = (valid_date - timedelta(days=1))
    if valid_date.weekday() == 5:  # if saturday
        valid_datetime = (valid_datetime - timedelta(days=1))
        valid_date = (valid_date - timedelta(days=1))
    if valid_date.weekday() == 6:  # if sunday
        valid_datetime = (valid_datetime - timedelta(days=2))
        valid_date = (valid_date - timedelta(days=2))
    if valid_date in holidays:
        valid_datetime = (valid_datetime - timedelta(days=1))
        valid_date = (valid_date - timedelta(days=1))
    e_date = valid_date

    n_interval = '1d' if interval == 'Daily' else '1wk' if interval == 'Weekly' else '1mo' if interval == 'Monthly' else '1y' if interval == 'Yearly' else interval

    if '1d' in n_interval:
        dates = (e_date - timedelta(days=75), e_date)  # 2 months worth of data
    elif '1wk' in n_interval:
        # change end date to a monday before
        cur_day = abs(e_date.weekday())
        if cur_day != 0:
            e_date = e_date - timedelta(days=cur_day + 2)
        # change begin date to a monday
        begin_date = e_date - timedelta(days=250)
        begin_day = abs(begin_date.weekday())
        if begin_day != 0:
            begin_date = begin_date - timedelta(days=begin_day)
        dates = (begin_date, e_date)  # ~5 months
    elif '1mo' in n_interval:
        dates = ((e_date - timedelta(days=600)).replace(day=1), e_date.replace(day=1))  # ~20 months
    elif '1y' not in n_interval:
        if n_interval == '5m':
            s_date = e_date - timedelta(days=2)
            if e_date.weekday() == 0:
                s_date = s_date - timedelta(days=2)
            dates = (s_date, e_date)  # month worth of data
        if n_interval == '15m':
            s_date = e_date - timedelta(days=4)
            if e_date.weekday() == 0:
                s_date = s_date - timedelta(days=2)
            dates = (s_date, e_date)  # month worth of data
        elif '30m' in n_interval:
            dates = (e_date - timedelta(days=6), e_date)  # month worth of data
        elif '60m' in n_interval:
            dates = (e_date - timedelta(days=8), e_date)  # month worth of data


    _has_actuals = has_actuals
    out = output
    # Generate Data for usage in display_model
    print('[INFO] Generating data used for sampler.')
    launch.sampler.set_ticker(ticker)
    data_task = launch.sampler.generate_sample(_has_actuals=has_actuals, force_generate=force_generate, out=out, rand_date=False, interval=n_interval,
                                        opt_fib_vals=opt_fib_vals)
    data = await gather(data_task)
    del data_task
    data = data[0]

    # Clear out specific axis, as there are multiple models outputted to the axis
    # dis.axes[0,1].clear()
    dis.clear_subplots()

    # BOX PLOT CALL
    box_plot_task = launch.display_model(nn_dict["new_scaled_2layer"],"new_scaled_2layer", has_actuals, ticker, 'green', force_generate, True, 0, 0, data, 0.05,
                         n_interval,opt_fib_vals,dis,skip_display,out)

    #
    # Model_Out_2 LABEL
    task1 = launch.display_model(
                nn_dict["new_scaled_2layer_v2"] if out == 1 else "","new_scaled_2layer_v2" if out == 1 else "",
        _has_actuals, ticker, 'green', force_generate, False, 0, 1, data,
                0.05, n_interval,[],dis,skip_display,out)
    gc.collect()
    await gather(box_plot_task, task1)
    del box_plot_task, task1
    dis.fig.canvas.draw()  # draw image before returning
    fig = dis.fig
    # print(fig.get_size_inches(),fig.dpi)
    axes = dis.axes
    return fig, axes

async def get_preview_prices(ticker: str, force_generation=False) -> str:
    try:
        data_gen = Generator()
        res = await data_gen.generate_quick_data(ticker, force_generation)
        del data_gen

        return res
    except Exception as e:
        print(f'[ERROR] No data generated for {ticker}!  Continuing...')
        return 'nan     nan'


async def find_all_big_moves(nn_dict: dict, tickers: list, force_generation=False, _has_actuals: bool = False, percent: float = 0.02,
                       interval: str = 'Daily') -> list:

    launch = launcher()

    # Confirm end date is valid
    valid_datetime = datetime.utcnow()
    holidays = USFederalHolidayCalendar().holidays(start=valid_datetime,
                                                   end=(valid_datetime - timedelta(days=7))).to_pydatetime()
    valid_date = valid_datetime.date()
    if (
            datetime.utcnow().hour <= 14 and datetime.utcnow().minute < 30):  # if current time is before 9:30 AM EST, go back a day
        valid_datetime = (valid_datetime - timedelta(days=1))
        valid_date = (valid_date - timedelta(days=1))

    if valid_date in holidays and 0 <= valid_date.weekday() <= 4:  # week day holiday
        valid_datetime = (valid_datetime - timedelta(days=1))
        valid_date = (valid_date - timedelta(days=1))
    if valid_date.weekday() == 5:  # if saturday
        valid_datetime = (valid_datetime - timedelta(days=1))
        valid_date = (valid_date - timedelta(days=1))
    if valid_date.weekday() == 6:  # if sunday
        valid_datetime = (valid_datetime - timedelta(days=2))
        valid_date = (valid_date - timedelta(days=2))
    if valid_date in holidays:
        valid_datetime = (valid_datetime - timedelta(days=1))
        valid_date = (valid_date - timedelta(days=1))
    e_date = valid_date

    n_interval = '1d' if interval == 'Daily' else '1wk' if interval == 'Weekly' else\
        '1mo' if interval == 'Monthly' else\
            '1y' if interval == 'Yearly' else interval

    if '1d' in n_interval:
        dates = (e_date - timedelta(days=75), e_date)  # month worth of data
    elif '1wk' in n_interval:
        cur_day = abs(e_date.weekday())
        if cur_day != 0:
            e_date = e_date - timedelta(days=cur_day + 2)
        # change begin date to a monday
        begin_date = e_date - timedelta(days=250)
        begin_day = abs(begin_date.weekday())
        if begin_day != 0:
            begin_date = begin_date - timedelta(days=begin_day)

        dates = (begin_date, e_date)  # ~5 months
    elif '1mo' in n_interval:
        dates = ((e_date - timedelta(months=15)).replace(day=1), e_date)  # ~20 months
    elif '1y' not in n_interval:
        if n_interval == '5m':
            dates = (e_date - timedelta(days=4), e_date)  # months worth of data
        if n_interval == '15m':
            dates = (e_date - timedelta(days=4), e_date)  # months worth of data
        if n_interval == '30m':
            dates = (e_date - timedelta(days=7), e_date)  # months worth of data
        if n_interval == '60m':
           dates = (e_date - timedelta(days=14), e_date)  # months worth of data
    path = Path(os.getcwd()).absolute()

    task_list = []
    for ticker in tickers:
        try:
            out = 4 # Change if needed
            await launch.gen.set_ticker(ticker)
            print("[INFO] Generating necessary data (stock data/ema/fib/keltner).")
            data = await launch.gen.generate_data_with_dates(dates[0], dates[1], False, force_generation, out, True, '1d', n_interval)
            # print(data,flush=True)
            print("[INFO] Preparing to generate & display model.")
            task_list.append(launch.display_model(
                    nn_dict["new_scaled_2layer"] if out == 1 else "","new_scaled_2layer" if out == 1 else "", _has_actuals, ticker, 'green', force_generation, False, 0, 1, data, False,
                    percent, n_interval,[],None,True,out))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f'{e}\n[ERROR] Could not generate an NN dataset for {ticker}!  Continuing...', flush=True)
            print(exc_type, fname, exc_tb.tb_lineno)
    [await task for task in task_list]
    saved_predictions: list = []
    while not launch.saved_predictions.empty():
        prediction = launch.saved_predictions.get()
        prior_close: int = prediction[2]
        if abs(((prior_close + prediction[1]) / prior_close) - 1) >= percent:
            saved_predictions.append(prediction)
    # After gathering all models, return
    return saved_predictions


if __name__ == "__main__":
    ticker = sys.argv[1]
    _has_actuals = sys.argv[2] == 'True'
    _force_generate = sys.argv[3] == 'True'
    loop = new_event_loop()
    neural_net = Network(0, 0)
    model_choices: list = [
        # 'relu_multilayer_l2', 'relu_2layer_0regularization', 'relu_2layer_l1l2', 'relu_1layer_l2',
        #                    'new_multi_analysis_l2', 'new_multi_analysis_2layer_0regularization',
        #                    'new_scaled_l2','new_scaled_l2_60m','new_scaled_l2_5m',
    'new_scaled_2layer',
    'new_scaled_2layer_v2']
    nn_models = [NN_Model(item) for item in model_choices]
    for model in nn_models:
        model.create_model(is_training=False)
    nn_dict: dict = {
        # 'relu_multilayer_l2': nn_models[0],
                     #      'relu_2layer_0regularization': nn_models[1],
                     #      'relu_2layer_l1l2': nn_models[2],
                     #      'relu_1layer_l2': nn_models[3],
                     # 'new_multi_analysis_l2': nn_models[4],
                     # 'new_multi_analysis_2layer_0regularization': nn_models[5],
                     # 'new_scaled_l2': nn_models[6],
                     # 'new_scaled_l2_60m': nn_models[7],
                     # 'new_scaled_l2_5m': nn_models[8],
                     'new_scaled_2layer': nn_models[0],
                    'new_scaled_2layer_v2': nn_models[1]
    }
    dis = Display()
    loop.run_until_complete(main(nn_dict=nn_dict,ticker=ticker,
                                 has_actuals=_has_actuals, force_generate=_force_generate,
                                 interval='1d',dis=dis,skip_display=False,output=4))