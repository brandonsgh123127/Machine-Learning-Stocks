import random

from V1.data_generator.normalize_data import Normalizer
import pandas as pd
import os
from pathlib import Path
import sys
import asyncio

'''
This class will retrieve any file given, and take a sample of data, and retrieve only a static subset for prediction analysis
'''


class Sample(Normalizer):
    def __init__(self, ticker=None, force_generate=False):
        super().__init__(ticker, force_generate=force_generate)
        self.DAYS_SAMPLED = 15
        self.ticker = ticker
        self.path = Path(os.getcwd()).absolute()

    def generate_sample(self, out=1, _has_actuals=False, rand_date=False, is_divergence=False, skip_db=False,
                        interval='1d', opt_fib_vals=[]):
        self.cnx = self.db_con.cursor(buffered=True)
        # 160 days used for multivariate
        self.DAYS_SAMPLED = self.days_map[interval]
        # If data has been set via neural_network, don't read data
        if self.data:
            pass
        else:
            print(f"[INFO] Generating ticker data for {self.ticker}.")
            # Read the current ticker data
            try:
                self.read_data(self.ticker, rand_dates=rand_date, out=out, skip_db=skip_db, interval=interval,
                               opt_fib_vals=opt_fib_vals)
            except Exception as e:
                raise Exception(f'[ERROR] Failed to read sample data for ticker {self.ticker}\r\nException: {e}')
        # Iterate through dataframe and retrieve random sample
        # Create dataframes for storing per model-basis
        try:
            print("[INFO] Calculating data that is important for model...")
            self.convert_derivatives(out=out)
        except Exception as e:
            print(f"[ERROR] Failed to calculate new row values for data!\r\nException: {e}")
            self.cnx.close()
            raise Exception(e)
        # Minimum amount of days sampled in df
        norm_data_list = self.unnormalized_data
        max_data = 20 # TODO: Move this outside to external function call.  Value used to keep certain amount of data split
        max_days = 5 if not _has_actuals else 6 # TODO: Same as above, max days per each sub batch
        for idx,data in enumerate(norm_data_list):
            self.unnormalized_data[idx] = self.unnormalized_data[idx].iloc[:, -max_days:]
        # Attempt normalization of data
        try:
            print("[INFO] Attempting to normalize data.")
            self.normalize(out=out)
        except Exception as e:
            print(f'[ERROR] Failure calling normalize function!\r\nException: {e}')
            raise Exception(e)
        # Now that we normalized, we need to do PCA, then feature extraction
        # Update: 7/29/23, although PCA is good for finding correlation,
        # Not good for Supervised learning.
        # try:
        #     print("[INFO] PCA calculation called.")
        #     self.pca()
        # except Exception as e:
        #     print(f"[ERROR] Failed to execute PCA\r\nException: {e}")
        #     raise Exception(e)
        self.cnx.close()

    def generate_divergence_sample(self, _has_actuals=False, rand_date=False, opt_fib_vals=[]):
        self.cnx = self.db_con.cursor(buffered=True)

        if not _has_actuals:
            self.DAYS_SAMPLED = 14
        else:
            self.DAYS_SAMPLED = 15
        # if data and keltner are populated, skip
        if self.data and self.keltner:
            pass
        else:
            # Read the current ticker data
            try:
                self.read_data(self.ticker, rand_dates=rand_date,
                               opt_fib_vals=opt_fib_vals)  # Get ticker and date from path
            except Exception as e:
                # print(f'[ERROR] Failed to read sample data for ticker {self.ticker}\r\nException: {str(e)}')
                raise Exception(f'[ERROR] Failed to read sample data for ticker {self.ticker}\r\nException: {str(e)}')
        # Iterate through dataframe and retrieve random sample
        self.convert_divergence()
        self.normalized_data = self.normalized_data.iloc[-(self.DAYS_SAMPLED):]

        rc = self.normalize_divergence()
        if rc == 1:
            raise Exception("Normalize did not return exit code 1")
        if len(self.normalized_data) < self.DAYS_SAMPLED:
            self.read_data(self.to_date, self.ticker, opt_fib_vals=opt_fib_vals)  # Get ticker and date from path
            self.convert_derivatives()
        self.cnx.close()
        return 0

    def unnormalize(self, data, out: int = 1, has_actuals=False):
        return super().unnormalize(data, out, has_actuals)

    '''
     Getters/Setters
    '''

    def set_ticker(self, ticker):
        self.ticker = ticker

    def get_ticker(self):
        return self.ticker

    def set_sample_data(self, data: pd.DataFrame, studies: pd.DataFrame, fib: pd.DataFrame, keltner: pd.DataFrame):
        self.data = data
        self.studies = studies
        self.fib = fib
        self.keltner = keltner

    def reset_data(self):
        del self.data, self.studies, self.fib, self.keltner, self.normalized_data, self.unnormalized_data
        self.data = []
        self.studies = []
        self.fib = []
        self.keltner = []
        self.normalized_data = []
        self.unnormalized_data = []
        self.studies = []

    def trim_data(self, has_actuals: bool = False):
        self.data = self.data.iloc[-30 if has_actuals else -29:]
        self.studies = self.studies.iloc[-30 if has_actuals else -29:]
        self.fib = self.fib.iloc[-30 if has_actuals else -29:]
        self.keltner = self.keltner.iloc[-30 if has_actuals else -29:]
        self.unnormalized_data = self.unnormalized_data.iloc[-30 if has_actuals else -29:]
        self.normalized_data = self.normalized_data.iloc[-30 if has_actuals else -29:]


if __name__ == '__main__':
    ticker_list:list = []
    path = Path(os.getcwd()).absolute()
    with open(f'{path}/data/watchlist/default.csv') as f:
        for i in range(1, 20):
            ticker = random.choice(f.readlines())
            ticker = ticker[0:ticker.find(',')]
            ticker_list.append(ticker)
            f.seek(0)
    for i in range(0, len(ticker_list)):
        sampler = Sample(ticker=ticker_list[i])
        sampler.generate_sample(out=4,skip_db=True,rand_date=True)
        print(sampler.fib)
    # for i in range(1,100000):
    #     indicator = sampler.generate_sample()
    #     if len(sampler.normalizer.normalized_data) < 15:
    #     print(indicator,len(sampler.normalizer.normalized_data))
# sampler.normalizer.display_line()
