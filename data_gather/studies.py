from data_gather._data_gather import Gather
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Studies(Gather):
    def __repr__(self):
        return 'stock_data.studies object <%s>' % ",".join(self.indicator)
    
    def __init__(self,indicator):
        Gather.__init__(self)
        Gather.set_indicator(self, indicator)
        self.applied_studies=pd.DataFrame()
        self.stock_data=pd.DataFrame()
        self.timeframe="1d"
    def set_timeframe(self,new_timeframe):
        self.timeframe = new_timeframe
    def get_timeframe(self):
        return self.timeframe
    def get_data(self):
        self.stock_data=Gather.get_data(self)
    def apply_ema(self, length, half=None):
        if half is not None:
            self.applied_studies= self.applied_studies.append(({f'ema{length}':self.stock_data.ewm(span=int(length),adjust=False,halflife=half).mean()}),ignore_index=True)
        else:
            self.applied_studies= self.applied_studies.append(({f'ema{length}':self.stock_data.ewm(span=int(length),adjust=False).mean()}),ignore_index=True)

studies = Studies("SPY")
Gather.set_data_from_range(studies,"01012020", "01012021")
studies.get_data()
studies.apply_ema("14")    