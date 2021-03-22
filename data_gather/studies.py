from data_gather._data_gather import Gather
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Studies(Gather):
    def __repr__(self):
        return 'stock_data.studies object <%s>' % ",".join(self.indicator)
    
    def __init__(self):
        pass