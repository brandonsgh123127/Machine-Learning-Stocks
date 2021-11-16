from pathlib import Path
import os
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
import random
from threading_impl.Thread_Pool import Thread_Pool
import threading
import time
import datetime
import sys

'''
    This class allows for unification of data, studies and news for future machine learning training.
    data formatting 
'''
class Generator():
    def __init__(self,ticker=None,path=None,force_generate=False):
        # print(ticker)
        self.studies = Studies(ticker,force_generate=force_generate)
        self.news=News_Scraper(ticker)
        self.thread_pool = Thread_Pool(amount_of_threads=2)
        if ticker is not None:
            self.ticker=ticker
        if path is not None:
            self.path = path
        else:
            self.path = Path(os.getcwd()).parent.absolute()

        
    def generate_data(self):
        # studies.__init__()
        with threading.Lock():
            studies = Studies(self.ticker)
            dates = studies.gen_random_dates()
            # Loop until valid data populates
            try:
                if studies.set_data_from_range(studies.date_set[0],studies.date_set[1],_force_generate=True) != 0 or studies.data.isnull().values.any() or len(studies.data) < 16:
                    print(f'[ERROR] Failed to generate data for {self.ticker}')
                    return 1
            except RuntimeError:
                print('[ERROR] Runtime Error when generating data!')
                pass

            # JSON PARAMETERS NEEDED TO BE PASSED TO TWITTER API
            query_param1 = {"query": "{}".format(self.ticker)}
            query_param2 = {"maxResults":"500"}
            query_param3 = {"fromDate":"{}".format(studies.date_set[0].strftime("%Y%m%d%H%M"))}
            query_param4 = {"toDate":"{}".format(studies.date_set[1].strftime("%Y%m%d%H%M"))}
            query_params = {}
            query_params.update(query_param1);query_params.update(query_param2);query_params.update(query_param3);query_params.update(query_param4)
        try:
            try:
                studies.data = studies.data.drop(['Volume'],axis=1)
            except:
                pass
            # studies.set_data_from_range(dates[0],dates[1])
            studies.apply_ema("14",self.studies.get_date_difference(dates[0],dates[1]))
            # studies.set_data_from_range(dates[0],dates[1])
            studies.apply_ema("30",self.studies.get_date_difference(dates[0],dates[1]))
            # studies.set_data_from_range(dates[0],dates[1])
        except Exception as e:
            print(f'[ERROR] Failed to generate ema studies for {self.ticker}!\n{str(e)}')
            return  
        try:
            studies.apply_fibonacci()
            studies.keltner_channels(20, 1.3, None)
        except Exception as e:
            print(f'[ERROR] Failed to generate fib/keltner studies for {self.ticker}!\n{str(e)}')
            return  
        del studies
        
        # Generates the P/L and percent of current day
    def generate_quick_data(self,ticker:str=None,force_generation=False):
        self.studies.set_indicator(ticker)
        if ticker is not None:
            self.ticker=ticker
        if datetime.datetime.utcnow().date().weekday() == 5:
            self.studies.set_data_from_range(datetime.datetime.utcnow() - datetime.timedelta(days=1) , datetime.datetime.utcnow(),_force_generate=force_generation)
        elif datetime.datetime.utcnow().date().weekday() == 6:
            self.studies.set_data_from_range(datetime.datetime.utcnow() - datetime.timedelta(days=2) , datetime.datetime.utcnow(),_force_generate=force_generation)
        elif datetime.datetime.utcnow().date().weekday() == 0: #monday
            self.studies.set_data_from_range(datetime.datetime.utcnow() - datetime.timedelta(days=3) , datetime.datetime.utcnow(),_force_generate=force_generation)
        else:
            self.studies.set_data_from_range(datetime.datetime.utcnow()- datetime.timedelta(days=1), datetime.datetime.utcnow(),_force_generate=force_generation)
        try:
            return [round(self.studies.data[['Close']].diff().iloc[1].to_list()[0],3),f'{round(self.studies.data[["Close"]].pct_change().iloc[1].to_list()[0]*100,3)}%']
        except Exception as e:
            print(f'[ERROR] Failed to gather quick data for {ticker}...\n',str(e))
            return ['n/a','n/a']
    def generate_data_with_dates(self,date1=None,date2=None,is_not_closed=False,force_generate=False,skip_db=False):
        self.studies = Studies(self.ticker,force_generate=force_generate)
        self.studies.date_set = (date1,date2)

        # Loop until valid data populates
        try:
            self.studies.set_data_from_range(date1,date2,force_generate,skip_db=skip_db)

            # self.studies.data = self.studies.data.reset_index()
        except Exception as e:
            print(f'[ERROR] Failed to generate data!\n',str(e))
            raise Exception
        # JSON PARAMETERS NEEDED TO BE PASSED TO TWITTER API
        query_param1 = {"query": "{}".format(self.ticker)}
        query_param2 = {"maxResults":"500"}
        query_param3 = {"fromDate":"{}".format(self.studies.date_set[0].strftime("%Y%m%d%H%M"))}
        query_param4 = {"toDate":"{}".format(self.studies.date_set[1].strftime("%Y%m%d%H%M"))}
        query_params = {}
        query_params.update(query_param1);query_params.update(query_param2);query_params.update(query_param3);query_params.update(query_param4)

        try:
            self.studies.data = self.studies.data.drop(['Volume'],axis=1)
        except:
            pass
        try:
            self.studies.data = self.studies.data.drop(['Adj Close'],axis=1)
        except:
            pass
        try:
            self.studies.data = self.studies.data.drop(['index'],axis=1)
        except:
            pass
        try:
            self.studies.data = self.studies.data.drop(['level_0'],axis=1)
        except:
            pass
        # print(self.studies.data)
        try:
            date_diff=self.studies.get_date_difference(self.studies.date_set[0],self.studies.date_set[1])
            self.studies.apply_ema("14",date_diff,skip_db=skip_db)
            # print(len(self.studies.data),len(self.studies.applied_studies['ema14']))
            self.studies.apply_ema("30",date_diff,skip_db=skip_db)
            self.studies.apply_fibonacci(skip_db=skip_db)
            self.studies.keltner_channels(20, 1.3, None,skip_db=skip_db)
            # Final join
          
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(f'[ERROR] Failed to generate studies for {self.ticker}!\n{str(e)}')
            return 
        return (self.studies.data,self.studies.applied_studies,self.studies.fibonacci_extension,self.studies.keltner)
    def get_ticker(self):
        return self.ticker
    def set_ticker(self,ticker):
        self.ticker = ticker
def choose_random_ticker(csv_file):
    with open(csv_file) as f:
        ticker = random.choice(f.readlines())
        ticker = ticker[0:ticker.find(',')]
        print(ticker)
        return ticker
def main():
    MAX_TICKERS=300
    MAX_ITERS=2
    path = Path(os.getcwd()).parent.absolute()
    for i in range(MAX_TICKERS):
        ticker = choose_random_ticker(f'{path}/data/watchlist/default.csv')
        generator = Generator(ticker,path)
        
        # Generate data        
        for j in range(MAX_ITERS):
            rc=generator.generate_data()
            while rc == 1:
                rc=generator.generate_data()
                time.sleep(j * (i/(MAX_ITERS/1.5)) + 0.5)
            time.sleep(j * (i/(MAX_ITERS/2)) + 1)
        del generator
        
    
if __name__ == '__main__':
    main()
    # generator = Generator("SPY",None)
    # print(generator.generate_quick_data())