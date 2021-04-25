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
from data_generator.normalize_data import Normalizer
from data_generator._data_generator import Generator
from data_generator.display_data import Display
import concurrent.futures
import datetime
import threading
import sys

listLock = threading.Lock()
def display_model(dis:Display,name:str= "model",_has_actuals:bool=False,ticker:str="spy",dates:list=[],color:str="blue"):
    data = load(f'{ticker}/{dates[0]}--{dates[1]}_data.csv',has_actuals=_has_actuals,name=f'{name}')
    with listLock:
        dis.read_studies_data(data[0],data[1])
    locs, labels = plt.xticks()
    plt.xticks(locs)
    if not _has_actuals: #if prediction, proceed
        dis.display_predict_only(ticker=ticker,dates=dates,color=f'{color}')
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
        dis3 = Display()
        with listLock:
            threads.append(executor.submit(display_model,dis3,"model_new_4",_has_actuals,ticker,dates,'magenta'))
        # concurrent.futures.wait(threads)
        if _has_actuals:        
            dis3 = threads[2].result()
            dis3.display_line(ticker=ticker,dates=dates,color="magenta")
            dis2 = threads[1].result()
            dis2.display_predict_only(ticker=ticker,dates=dates,color="black")
            dis1 = threads[0].result()
            dis1.display_predict_only(ticker=ticker,dates=dates,color="green")
            
        # Finally save the model
    plt.savefig(f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict.png')
    print(str(dates[0]),str(dates[1]))
if __name__ == "__main__":
    _has_actuals = sys.argv[2] == 'True'
    _is_not_closed =sys.argv[3] == 'True'
    vals = None
    if _is_not_closed:
        vals = (sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7])
    main(ticker=sys.argv[1],has_actuals=_has_actuals,is_not_closed=_is_not_closed,vals=vals)