import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
from pathlib import Path
import os
import pandas as pd
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

listLock = threading.Lock()
type = None
def display_model(dis:Display,name:str= "model",_has_actuals:bool=False,ticker:str="spy",dates:list=[],color:str="blue",unnormalized_data = False):
    if 'divergence' not in name:
        data = load(f'{ticker}/{dates[0]}--{dates[1]}_data.csv',has_actuals=_has_actuals,name=f'{name}')
    else:
        # print('divergence')
        data = load_divergence(f'{ticker}/{dates[0]}--{dates[1]}_data.csv',has_actuals=_has_actuals,name=f'{name}')
    with listLock:
        # print(data)
        dis.read_studies_data(data[0],data[1])
    locs, labels = plt.xticks()
    plt.xticks(locs)
    if not _has_actuals: #if prediction, proceed
        if not unnormalized_data:
            if 'divergence' not in name:
                dis.display_predict_only(ticker=ticker,dates=dates,color=f'{color}')
            else:
                # print('divergence dis')
                dis.display_divergence(ticker=ticker,dates=dates,color=f'{color}')
        else:
            if 'divergence' not in name:
                dis.display_box(data[2])
    return dis
def main(ticker:str = "spy",has_actuals:bool = True, is_not_closed:bool = False,vals:str=None):
    if ticker is not None:
        ticker = ticker
    else:
        ticker = "dash"
    path = Path(os.getcwd()).parent.absolute()
    
    gen = Generator(ticker,path)
    gen.studies.set_indicator(f'{ticker}')
    # if current trading day, set prediction for tomorrow in date name
    dates = []
    if is_not_closed: #same day prediction
        # print('same day')
        dates = (datetime.date.today() - datetime.timedelta(days = 50), datetime.date.today() + datetime.timedelta(days = 1)) #month worth of data
    else:
        dates = (datetime.date.today() - datetime.timedelta(days = 50), datetime.date.today() + datetime.timedelta(days = 0)) #month worth of data
    
    _has_actuals = has_actuals
    gen.generate_data_with_dates(dates[0],dates[1],is_not_closed=is_not_closed,vals=vals)
    if type == 'predict':
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            threads = []
            #OK MODEL
            dis1 = Display()
            with listLock:
                threads.append(executor.submit(display_model,dis1,"model_new_2",_has_actuals,ticker,dates,'green'))
            #Direction Bias model
            dis2 = Display()
            with listLock:
                threads.append(executor.submit(display_model,dis2,"model_new_3",_has_actuals,ticker,dates,'black'))
            #NEW relu-based model
            dis4 = Display()
            with listLock:
                threads.append(executor.submit(display_model,dis4,"model_new_5",_has_actuals,ticker,dates,'blue'))
            dis3 = Display()
            with listLock:
                threads.append(executor.submit(display_model,dis3,"model_new_4",_has_actuals,ticker,dates,'magenta'))
                
            # concurrent.futures.wait(threads)
            if _has_actuals:        
                dis3 = threads[3].result()
                dis3.display_line(ticker=ticker,dates=dates,color="magenta")
                dis4 = threads[2].result()
                dis4.display_line(ticker=ticker,dates=dates,color="blue")
                dis2 = threads[1].result()
                dis2.display_predict_only(ticker=ticker,dates=dates,color="black")
                dis1 = threads[0].result()
                dis1.display_predict_only(ticker=ticker,dates=dates,color="green")
        if not has_actuals:
            plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict.png')
        else:
            plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_a.png')

        plt.cla()
        exit(0)
    elif type == 'divergence':
        threads = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            dis5 = Display()
            # with listLock:
                # threads.append(executor.submit(display_model,dis5,"divergence",_has_actuals,ticker,dates,'green'))
            # dis6 = Display()
            # with listLock:
                # threads.append(executor.submit(display_model,dis6,"divergence_2",_has_actuals,ticker,dates,'black'))
            # dis7 = Display()
            # with listLock:
                # threads.append(executor.submit(display_model,dis7,"divergence_3",_has_actuals,ticker,dates,'blue'))
            dis8 = Display()
            with listLock:
                threads.append(executor.submit(display_model,dis8,"divergence_4",_has_actuals,ticker,dates,'magenta'))
            if _has_actuals:
                dis8 = threads[0].result()
                dis8.display_divergence(ticker=ticker,dates=dates,color=f'm',has_actuals=_has_actuals)
        print(str(dates[0]),str(dates[1]))
        if not has_actuals:
            plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence.png')
        else:
            plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence_a.png')
        plt.cla()
        exit(0)
    elif type == 'u':
        dis9 = Display()
        dis9 = display_model(dis9,"model_new_2",False,ticker,dates,'green',True)
        if not has_actuals:
            plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_u.png')
        else:
            plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_u_a.png')
        plt.cla()
        exit(0)
if __name__ == "__main__":
    type = sys.argv[1]
    _has_actuals = sys.argv[3] == 'True'
    _is_not_closed =sys.argv[4] == 'True'
    vals = None
    if _is_not_closed:
        vals = (sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8])
    main(ticker=sys.argv[2],has_actuals=_has_actuals,is_not_closed=_is_not_closed,vals=vals)