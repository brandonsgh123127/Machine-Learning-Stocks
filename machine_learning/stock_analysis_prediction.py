import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
from data_generator._data_generator import Generator
from pathlib import Path
import os
import matplotlib.pyplot as plt
from machine_learning.neural_network import Network
from machine_learning.neural_network import load
from machine_learning.neural_network_divergence import load_divergence
from data_generator.normalize_data import Normalizer
from data_generator._data_generator import Generator
from data_generator.display_data import Display
import concurrent.futures
import datetime
import threading
import sys
# import json
import time
import queue
import gc
from threading_impl.Thread_Pool import Thread_Pool
import PIL
from pandas.tseries.holiday import USFederalHolidayCalendar


class launcher():
    def __init__(self):
        self._type = None
        plt.cla()
        plt.clf()
        self.dis:Display = Display()
        self.listLock=threading.Lock()
    
    def display_model(self,name:str= "model_relu",_has_actuals:bool=False,ticker:str="spy",color:str="blue",force_generation=False,unnormalized_data = False,row=0,col=1):
        # Load machine learning model either based on divergence or not
        if 'divergence' not in name:
            data = load(f'{ticker.upper()}',has_actuals=_has_actuals,name=f'{name}',force_generation=force_generation,device_opt='/device:GPU:0')
        else:
            data = load_divergence(f'{ticker.upper()}',has_actuals=_has_actuals,force_generation=force_generation,device_opt='/device:GPU:0')
        # read data for loading into display portion
        if 'divergence' not in name:
            with self.listLock:
                self.dis.read_studies_data(data[0],data[1],data[3],data[4])
        else:
            with self.listLock:
                self.dis.read_studies_data(data[0],data[1],data[2],data[3])
        # display data
        if not _has_actuals: #if prediction, proceed
            if not unnormalized_data:
                if 'divergence' in name:
                    with self.listLock:
                        self.dis.display_divergence(color=f'{color}',row=1,col=1)
                else:
                    with self.listLock:
                        self.dis.display_predict_only(color=f'{color}',row=row,col=col)
            else:
                with self.listLock:
                    self.dis.display_box(data[2],has_actuals=_has_actuals)
        else:
            if unnormalized_data:
                with self.listLock:
                    self.dis.display_box(data[2],has_actuals=_has_actuals)
            else:
                if 'divergence' in name:
                    with self.listLock:
                        self.dis.display_divergence(color=f'{color}',row=1,col=1)
                else:
                    with self.listLock:
                        self.dis.display_line(color=f'{color}',row=row,col=col)
    

data_gen = Generator()

def main(ticker:str = "SPY",has_actuals:bool = True,force_generate=False):
    thread_pool = Thread_Pool(amount_of_threads=4)
    listLock = threading.Lock()


    launch = launcher()
    if ticker is not None:
        ticker = ticker
    else:
        raise ValueError("Failed to find ticker name!")
    path = Path(os.getcwd()).parent.absolute()
    
    
    gen = Generator(ticker.upper(),path,force_generate)
    # if current trading day, set prediction for tomorrow in date name
    dates = []
    if not has_actuals: #predict next day
        dates = (datetime.date.today() - datetime.timedelta(days = 75), datetime.date.today() + datetime.timedelta(days = 1)) #month worth of data
    else:
        valid_datetime=datetime.datetime.now()
        
        # Confirm end date is valid 
        holidays=USFederalHolidayCalendar().holidays(start=valid_datetime - datetime.timedelta(days=75),end=valid_datetime).to_pydatetime()
        valid_date=valid_datetime.date()
        if valid_date in holidays and valid_date.weekday() >= 0 and valid_date.weekday() <= 4: #week day holiday
            valid_date = (valid_date - datetime.timedelta(days=1))
        if valid_date.weekday()==5: # if saturday
            valid_date = (valid_date - datetime.timedelta(days=1))
        if valid_date.weekday()==6: # if sunday
            valid_date = (valid_date - datetime.timedelta(days=2))
        if valid_date in holidays:
            valid_date = (valid_date - datetime.timedelta(days=1))
        e_date=valid_date
        
        
        dates = (datetime.date.today() - datetime.timedelta(days = 75), e_date ) #month worth of data
    
    _has_actuals = has_actuals
    try:
        # print(f'{dates[0]} to {dates[1]}')
        gen.generate_data_with_dates(dates[0],dates[1],force_generate=force_generate)
    except Exception as e:
        print(f'[ERROR] Failed to generate data for dates ranging from {dates[0]} to {dates[1]}!\nException:\n',str(e),flush=True)
        raise Exception(str(e))
    # 
    # PREDICT LABEL
    
    # Call display line on first result, rest display predict only
    if _has_actuals:
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_relu",_has_actuals,ticker,'green',force_generate,False,1,0))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_leaky",_has_actuals,ticker,'black',force_generate,False,1,0))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_sigmoid",_has_actuals,ticker,'magenta',force_generate,False,1,0))) == 1:
                thread_pool.join_workers()

    # Call solely display predict only
    else:
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_relu",_has_actuals,ticker,'green',force_generate,False,1,0))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_leaky",_has_actuals,ticker,'black',force_generate,False,1,0))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_sigmoid",_has_actuals,ticker,'magenta',force_generate,False,1,0))) == 1:
                thread_pool.join_workers()
    gc.collect()
    thread_pool.join_workers()
    #
    # DIVERGENCE LABEL
    with listLock:
        while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("divergence",_has_actuals,ticker,'magenta',force_generate,False,1,1))) == 1:
            thread_pool.join_workers()
        thread_pool.join_workers()
        # dis.display_divergence(color=f'm',has_actuals=_has_actuals,row=1,col=1)
    gc.collect()

    #
    # CHART LABEL
    launch.display_model("model_relu",has_actuals,ticker,'green',force_generate,True,0,0)
    gc.collect()

    #
    # Model_Out_2 LABEL
    if _has_actuals:
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_relu2",_has_actuals,ticker,'green',force_generate,False,0,1))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_leaky2",_has_actuals,ticker,'black',force_generate,False,0,1))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_sigmoid2",_has_actuals,ticker,'magenta',force_generate,False,0,1))) == 1:
                thread_pool.join_workers()
    else:
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_relu2",_has_actuals,ticker,'green',force_generate,False,0,1))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_leaky2",_has_actuals,ticker,'black',force_generate,False,0,1))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=launch.display_model,args=("model_sigmoid2",_has_actuals,ticker,'magenta',force_generate,False,0,1))) == 1:
                thread_pool.join_workers()

    gc.collect()
    thread_pool.join_workers()
    
    launch.dis.fig.canvas.draw() # draw image before returning
    return (launch.dis.fig,launch.dis.axes)
    # return PIL.Image.frombytes('RGB',launch.dis.fig.canvas.get_width_height(),launch.dis.fig.canvas.tostring_rgb()) #Return Canvas as image in output

def get_preview_prices(ticker:str,force_generation=False):
    return data_gen.generate_quick_data(ticker,force_generation)
if __name__ == "__main__":
    _type = sys.argv[1]
    _has_actuals = sys.argv[3] == 'True'
    # print(_type,_has_actuals,_is_not_closed)
    main(ticker=sys.argv[2],has_actuals=_has_actuals)
