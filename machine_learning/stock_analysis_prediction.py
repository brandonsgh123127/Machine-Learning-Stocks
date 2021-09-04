import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
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
listLock = threading.Lock()
_type = None
dis_queue = queue.Queue()
data_queue = queue.Queue()
thread_pool = Thread_Pool(amount_of_threads=3)

def display_model(dis:Display,name:str= "model_relu",_has_actuals:bool=False,ticker:str="spy",dates:list=[],color:str="blue",is_predict=False,unnormalized_data = False):
    global dis_queue
    global data_queue
    # Load machine learning model either based on divergence or not
    if 'divergence' not in name:
        data = load(f'{ticker}/{dates[0]}--{dates[1]}_data.csv',has_actuals=_has_actuals,name=f'{name}',_is_predict=is_predict,device_opt='/device:CPU:0')
    else:
        data = load_divergence(f'{ticker}/{dates[0]}--{dates[1]}_data.csv',has_actuals=_has_actuals,name=f'{name}',device_opt='/device:CPU:0')
    # read data for loading into display portion
    if 'divergence' not in name:
        dis.read_studies_data(data[0],data[1],data[3],data[4])
    else:
        dis.read_studies_data(data[0],data[1],data[2],data[3])
    locs, labels = plt.xticks()
    plt.xticks(locs)
    # display data
    if not _has_actuals: #if prediction, proceed
        if not unnormalized_data:
            if 'divergence' in name:
                dis.display_divergence(ticker=ticker,dates=dates,color=f'{color}')
        else:
            dis.display_box(data[2])
    else:
        if unnormalized_data:
            dis.display_box(data[2])
    dis_queue.put(dis)
    data_queue.put((data[0],data[1],data[2])) # Data[2] will be the unnormalized predicted open/close... most useful
def main(ticker:str = "SPY",has_actuals:bool = True, is_not_closed:bool = False,vals:tuple=None,opn:str=None,high:str=None,low:str=None,close:str=None,tpe:str=None):
    global dis_queue,data_queue
    global _type
    data_queue = queue.Queue()
    dis_queue = queue.Queue()
    thread_pool = Thread_Pool(amount_of_threads=4)

    if type is not None: # passed from launch_main
        _type=tpe
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
        dates = (datetime.date.today() - datetime.timedelta(days = 50), datetime.date.today()) #month worth of data
    else:
        dates = (datetime.date.today() - datetime.timedelta(days = 50), datetime.date.today() + datetime.timedelta(days = 1)) #month worth of data
    
    _has_actuals = has_actuals
    try:
        # print(f'{dates[0]} to {dates[1]}')
        gen.generate_data_with_dates(dates[0],dates[1],is_not_closed=is_not_closed,vals=vals)
    except Exception as e:
        print(f'[ERROR] Failed to generate data for dates ranging from {dates[0]} to {dates[1]}!\nException:\n',str(e),flush=True)
        raise Exception(str(e))
    if _type == 'predict':
        dis1 = Display()
        with listLock:
            thread_pool.start_worker(threading.Thread(target=display_model,args=(dis1,"model_relu",_has_actuals,ticker,dates,'green',is_not_closed)))
        dis1=dis_queue.get()
        dis2 = Display()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=(dis2,"model_leaky",_has_actuals,ticker,dates,'black',is_not_closed))) == 1:
                time.sleep(3)
                thread_pool.join_workers()
        dis2=dis_queue.get()
        dis3 = Display()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=(dis3,"model_sigmoid",_has_actuals,ticker,dates,'magenta',is_not_closed))) == 1:
                time.sleep(3)
                thread_pool.join_workers()
        dis3 = dis_queue.get()
        
        dis_queue = queue.Queue()
        if _has_actuals:   
            thread_pool.join_workers()     
            dis3.display_line(ticker=ticker,dates=dates,color="magenta")
            dis2.display_predict_only(ticker=ticker,dates=dates,color="black")
            dis1.display_predict_only(ticker=ticker,dates=dates,color="green")
            plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_actual.png')
        else:
            thread_pool.join_workers()
            dis3.display_predict_only(ticker=ticker,dates=dates,color="magenta")
            dis2.display_predict_only(ticker=ticker,dates=dates,color="black")
            dis1.display_predict_only(ticker=ticker,dates=dates,color="green")
            if is_not_closed == False:
                plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict.png')
            else:
                plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict-pred.png')
        plt.clf()
        plt.cla()
        del dis2
        del dis3
        gc.collect()
    elif 'divergence' == _type:
        dis8 = Display()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=(dis8,"divergence_3",_has_actuals,ticker,dates,'magenta',is_not_closed))) == 1:
                time.sleep(3)
                thread_pool.join_workers()
            thread_pool.join_workers()
            dis8=dis_queue.get()
            dis8.display_divergence(ticker=ticker,dates=dates,color=f'm',has_actuals=_has_actuals)
        if not has_actuals:
            if not is_not_closed:
                plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence.png')
            else:
                plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence-pred.png')
        else:
            plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence_actual.png')
        plt.clf()
        plt.cla()
        del dis8 
        gc.collect()
    elif _type == 'chart':
        dis9 = Display()
        dis9 = display_model(dis9,"model_relu",has_actuals,ticker,dates,'green',is_not_closed,True)
        if not has_actuals:
            plt.tight_layout()
            if is_not_closed == False:
                plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_chart.png')
            else:
                plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_chart-pred.png')
        else:
            plt.tight_layout()
            plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_chart_actual.png')
        plt.clf()
        plt.cla()
        del dis9
        gc.collect()
    elif _type == 'model_out_2':
        dis10 = Display()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=(dis10,"model_relu2",_has_actuals,ticker,dates,'green',is_not_closed))) == 1:
                time.sleep(3)
                thread_pool.join_workers()
        dis11 = Display()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=(dis11,"model_leaky2",_has_actuals,ticker,dates,'black',is_not_closed))) == 1:
                time.sleep(3)
                thread_pool.join_workers()
        dis12 = Display()
        with listLock:
            while thread_pool.start_worker(threading.Thread(target=display_model,args=(dis12,"model_sigmoid2",_has_actuals,ticker,dates,'magenta',is_not_closed))) == 1:
                time.sleep(3)
                thread_pool.join_workers()
        dis10=dis_queue.get()
        dis11=dis_queue.get()
        dis12=dis_queue.get()
        if not _has_actuals:
            thread_pool.join_workers()
            dis12.display_predict_only(ticker=ticker,dates=dates,color=f'magenta')
            dis11.display_predict_only(ticker=ticker,dates=dates,color=f'black')
            dis10.display_predict_only(ticker=ticker,dates=dates,color=f'green')
            if not is_not_closed:
                plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_2.png')
            else:
                plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_2-pred.png')
        else:
            thread_pool.join_workers()
            dis12.display_line(ticker=ticker,dates=dates,color=f'magenta')
            dis11.display_line(ticker=ticker,dates=dates,color=f'black')
            dis10.display_predict_only(ticker=ticker,dates=dates,color=f'green')
            plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_2_actual.png')
        plt.clf()
        plt.cla()
        del dis10
        del dis11 
        del dis12
        gc.collect()
    return (ticker,data_queue)#Return Data from machine learning models
if __name__ == "__main__":
    _type = sys.argv[1]
    _has_actuals = sys.argv[3] == 'True'
    _is_not_closed =sys.argv[4] == 'True'
    vals = None
    # print(_type,_has_actuals,_is_not_closed)
    if _is_not_closed:
        vals = (sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8])
    main(ticker=sys.argv[2],has_actuals=_has_actuals,is_not_closed=_is_not_closed,vals=vals)
