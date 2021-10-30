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

listLock = threading.Lock()
_type = None
thread_pool = Thread_Pool(amount_of_threads=4)
data_gen = Generator()
dis:Display = Display()

def display_model(name:str= "model_relu",_has_actuals:bool=False,ticker:str="spy",dates:list=[],color:str="blue",is_predict=False,unnormalized_data = False,row=0,col=1):
    global dis
    # Load machine learning model either based on divergence or not
    if 'divergence' not in name:
        data = load(f'{ticker.upper()}',has_actuals=_has_actuals,name=f'{name}',_is_predict=is_predict,device_opt='/device:CPU:0')
    else:
        data = load_divergence(f'{ticker}/{dates[0]}--{dates[1]}_data.csv',has_actuals=_has_actuals,name=f'{name}',device_opt='/device:CPU:0')
    # read data for loading into display portion
    if 'divergence' not in name:
        dis.read_studies_data(data[0],data[1],data[3],data[4])
    else:
        dis.read_studies_data(data[0],data[1],data[2],data[3])
    # display data
    if not _has_actuals: #if prediction, proceed
        if not unnormalized_data:
            if 'divergence' in name:
                dis.display_divergence(ticker=ticker,dates=dates,color=f'{color}',row=1,col=1)
            else:
                dis.display_predict_only(ticker=ticker,dates=dates,color=f'{color}',row=row,col=col)
        else:
            dis.display_box(data[2])
    else:
        if unnormalized_data:
            dis.display_box(data[2])
        else:
            if 'divergence' in name:
                dis.display_divergence(ticker=ticker,dates=dates,color=f'{color}',row=1,col=1)
            else:
                dis.display_line(ticker=ticker,dates=dates,color=f'{color}',row=row,col=col)

def main(ticker:str = "SPY",has_actuals:bool = True, is_not_closed:bool = False,vals:tuple=None,opn:str=None,high:str=None,low:str=None,close:str=None):
    global _type
    global dis
    global thread_pool
    
    if vals is None and opn is not None: # passed from launch_main
        vals = (opn,high,low,close)
    if ticker is not None:
        ticker = ticker
    else:
        raise ValueError("Failed to find ticker name!")
    path = Path(os.getcwd()).parent.absolute()
    
    
    gen = Generator(ticker.upper(),path)
    gen.studies.set_indicator(f'{ticker.upper()}')
    # if current trading day, set prediction for tomorrow in date name
    dates = []
    if is_not_closed: #predict next day
        dates = (datetime.date.today() - datetime.timedelta(days = 75), datetime.date.today() + datetime.timedelta(days = 1)) #month worth of data
    else:
        dates = (datetime.date.today() - datetime.timedelta(days = 75), datetime.date.today() ) #month worth of data
    
    _has_actuals = has_actuals
    try:
        # print(f'{dates[0]} to {dates[1]}')
        gen.generate_data_with_dates(dates[0],dates[1],is_not_closed=is_not_closed,vals=vals)
    except Exception as e:
        print(f'[ERROR] Failed to generate data for dates ranging from {dates[0]} to {dates[1]}!\nException:\n',str(e),flush=True)
        raise Exception(str(e))
    # 
    # PREDICT LABEL
    
    # Call display line on first result, rest display predict only
    if _has_actuals:
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_relu",_has_actuals,ticker,dates,'green',is_not_closed,False,1,0))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_leaky",False,ticker,dates,'black',is_not_closed,False,1,0))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_sigmoid",False,ticker,dates,'magenta',is_not_closed,False,1,0))) == 1:
                thread_pool.join_workers()

    # Call solely display predict only
    else:
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_relu",_has_actuals,ticker,dates,'green',is_not_closed,False,1,0))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_leaky",_has_actuals,ticker,dates,'black',is_not_closed,False,1,0))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_sigmoid",_has_actuals,ticker,dates,'magenta',is_not_closed,False,1,0))) == 1:
                thread_pool.join_workers()
    gc.collect()
    thread_pool.join_workers()
    #
    # DIVERGENCE LABEL
    with listLock:
        while thread_pool.start_worker(threading.Thread(target=display_model,args=("divergence_3",_has_actuals,ticker,dates,'magenta',is_not_closed))) == 1:
            thread_pool.join_workers()
        thread_pool.join_workers()
        dis.display_divergence(ticker=ticker,dates=dates,color=f'm',has_actuals=_has_actuals)
    gc.collect()

    #
    # CHART LABEL
    display_model("model_relu",has_actuals,ticker,dates,'green',is_not_closed,True)
    gc.collect()

    #
    # Model_Out_2 LABEL
    if _has_actuals:
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_relu2",_has_actuals,ticker,dates,'green',is_not_closed,False,0,1))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_leaky2",False,ticker,dates,'black',is_not_closed,False,0,1))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_sigmoid2",False,ticker,dates,'magenta',is_not_closed,False,0,1))) == 1:
                thread_pool.join_workers()
    else:
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_relu2",_has_actuals,ticker,dates,'green',is_not_closed,False,0,1))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_leaky2",_has_actuals,ticker,dates,'black',is_not_closed,False,0,1))) == 1:
                thread_pool.join_workers()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=("model_sigmoid2",_has_actuals,ticker,dates,'magenta',is_not_closed,False,0,1))) == 1:
                thread_pool.join_workers()

    gc.collect()
    thread_pool.join_workers()
    
    dis.fig.canvas.draw() # draw image before returning
    return PIL.Image.frombytes('RGB',dis.fig.canvas.get_width_height(),dis.fig.canvas.tostring_rgb()) #Return Canvas as image in output

def get_preview_prices(ticker:str):
    return data_gen.generate_quick_data(ticker)
if __name__ == "__main__":
    _type = sys.argv[1]
    _has_actuals = sys.argv[3] == 'True'
    _is_not_closed =sys.argv[4] == 'True'
    vals = None
    # print(_type,_has_actuals,_is_not_closed)
    if _is_not_closed:
        vals = (sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8])
    main(ticker=sys.argv[2],has_actuals=_has_actuals,is_not_closed=_is_not_closed,vals=vals)
