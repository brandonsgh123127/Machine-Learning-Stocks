import yfinance as yf
import datetime
from pandas_datareader import data as pdr
import twitter
import random
import pytz
import os,sys
import requests
import mysql.connector
from pathlib import Path
import xml.etree.ElementTree as ET
from mysql.connector import errorcode
import binascii
import uuid


'''CORE CLASS IMPLEMENTATION--

    Gather class allows for basic functions within other modules, these functions are:
    date retrieval
    stock retrieval
    news retrieval through twitter api
    
'''
class Gather():
    db_con:mysql.connector = None
    cnx:mysql.connector.cursor = None
    MAX_DATE = datetime.datetime.now().date()
    MIN_DATE = datetime.datetime(2013,1,1).date()
    MIN_RANGE = 50 # at least 7 days generated
    MAX_RANGE = 200 # at most 1 month to look at trend
    DAYS_IN_MONTH = {1:31,
                     2:28,
                     3:31,
                     4:30,
                     5:31,
                     6:30,
                     7:31,
                     8:31,
                     9:30,
                     10:31,
                     11:30,
                     12:31}
    search_url = "https://api.twitter.com/1.1/tweets/search/fullarchive/dev.json"

    def __repr__(self):
        return 'stock_data.gather_data object <%s>' % ",".join(self.indicator)
    def __init__(self):
        '''
        Utilize a config file to establish a mysql connection to the database
        '''
        self.new_uuid_gen = None
        self.path = Path(os.getcwd()).parent.absolute()
        tree = ET.parse("{0}/data/mysql/mysql_config.xml".format(self.path))
        root = tree.getroot()
        # Connect
        try:
            self.db_con = mysql.connector.connect(
              host="127.0.0.1",
              user=root[0].text,
              password=root[1].text,
              raise_on_warnings = True,
              database='stocks',
              charset = 'latin1'
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
                
        self.cnx = self.db_con.cursor(buffered=True)
        # self.cnx.execute('SHOW TABLES FROM stocks;')
        yf.pdr_override()
        # Local API Key for twitter account
        self.api = twitter.Api(consumer_key="wQ6ZquVju93IHqNNW0I4xn4ii",
                          consumer_secret="PorwKI2n1VpHznwyC38HV8a9xoDMWko4mOIDFfv2q7dQsFn2uY",
                          access_token_key="1104618795115651072-O3LSWBFVEPENGiTnXqf7cTtNgmNqUF",
                          access_token_secret="by7SUTtNPOYgAws0yliwk9YdiWIloSdv8kYX0YKic28UE",
                          sleep_on_rate_limit="true")
        self.indicator = ""
        self.data = []
        self.date_set = ()
        self.bearer="AAAAAAAAAAAAAAAAAAAAAJdONwEAAAAAzi2H1WrnhmAddAQKwveAfRN1DAY%3DdSFsj3bTRnDqqMxNmnxEKTG6O6UN3t3VMtnC0Y7xaGxqAF1QVq"
        self.headers = {"Authorization": "Bearer {0}".format(self.bearer), "content-type": "application/json",'Accept-encoding': 'gzip',
               'User-Agent': 'twitterdev-search-tweets-python/'}
    def set_indicator(self,indicator):
        self.indicator = indicator
    def get_indicator(self):
        return self.indicator    
    # retrieve pandas_datareader object of datetime
    def set_data_from_range(self,start_date,end_date):
        try:
            self.cnx = self.db_con.cursor(buffered=True)
            sys.stdout = open(os.devnull, 'w')
            self.data = pdr.get_data_yahoo(self.indicator,start=start_date.strftime("%Y-%m-%d"),end=end_date.strftime("%Y-%m-%d"))
            sys.stdout = sys.__stdout__
            if self.data.empty:
                return 1
            uuid_gen = uuid.uuid4()
            # Retrieve query from database, confirm that stock is in database, else make new query
            select_stmt = "SELECT `id` FROM stocks.stock WHERE stock like %(stock)s"
            resultado = self.cnx.execute(select_stmt, { 'stock': self.indicator},multi=True)
            for result in resultado:
                # print(len(result.fetchall()))
                # Query new stock, id
                res = result.fetchall()
                if len(res) == 0:
                    insert_stmt = """INSERT INTO stocks.stock (id, stock) 
                                VALUES (%(uuid)s,%(stock)s)"""
                    try:
                        # print('[INFO] inserting')
                        insert_resultado = self.cnx.execute(insert_stmt, { 'stock': self.indicator,
                                                                          'uuid':uuid_gen.bytes},multi=True)
                        self.db_con.commit()
                        # print('[INFO] Success')
                    except Exception as e:
                        print(f'[ERROR] Failed to insert stock named {self.indicator} into database!\nException:\n',str(e))
                else:
                    for r in res:
                        # print(f'{r[0]}\n')
                        # print(repr(binascii.b2a_hex(str.encode(r[0]))))
                        self.new_uuid_gen = binascii.b2a_hex(str.encode(r[0]))

           
            #Append dates to database
            for index, row in self.data.iterrows():
                insert_date_stmt = """INSERT INTO `stocks`.`data` (`data-id`, `stock-id`, `date`,`open`,high,low,`close`,`adj-close`) 
                VALUES (AES_ENCRYPT(%(stock)s, UNHEX(SHA2('stock-id',512))),
                %(stock_id)s,DATE(%(Date)s),%(Open)s,%(High)s,%(Low)s,%(Close)s,%(Adj Close)s)"""
                try:
                    if self.new_uuid_gen is None:
                        insert_date_resultado = self.cnx.execute(insert_date_stmt, { 'stock': f'{self.indicator}{str(row.name)}',
                                                                                'stock_id':uuid_gen.bytes,
                                                                                'Date':str(row.name),
                                                                                'Open':row['Open'],
                                                                                'High':row['High'],
                                                                                'Low':row['Low'],
                                                                                'Close':row['Close'],
                                                                                'Adj Close': row['Adj Close']},multi=True)
                    else:
                        insert_date_resultado = self.cnx.execute(insert_date_stmt, { 'stock': f'{self.indicator}{str(row.name)}',
                                                                                'stock_id':self.new_uuid_gen,
                                                                                'Date':str(row.name),
                                                                                'Open':row['Open'],
                                                                                'High':row['High'],
                                                                                'Low':row['Low'],
                                                                                'Close':row['Close'],
                                                                                'Adj Close': row['Adj Close']},multi=True)
                    # for result in resultado:
                        # print(result.statement)

                    
                    # print('[INFO] Successfully added date')
                except mysql.connector.errors.IntegrityError:
                    pass
                except Exception as e:
                    print(f'[ERROR] Failed to insert date for {self.indicator} into database!\nException:\n',str(e))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
            try:
                self.db_con.commit()
            except Exception as e:
                print('[Error] Could not commit changes!\nReason:\n',str(e))
                

        except Exception as e:
            print('[ERROR] Unknown Exception (Oh No)!\nException:\n',str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.cnx.close()
            return 1
        self.cnx.close()
        return 0
    def _reorder_dates(self,date1,date2):
        if date1 < date2:
            return (date1,date2) 
        else:
            return (date2,date1)
    # Generate random date for data generation
    def gen_random_dates(self):
        calc_leap_day = lambda year_month: random.randint(1,29) if year_month[1]==2 and ((year_month[0]%4==0 and year_month[0]%100==0 and year_month[0]%400==0) or (year_month[0]%4==0 and year_month[0]%100!=0)) else random.randint(1,28) if year_month[1]==2 else random.randint(1,self.DAYS_IN_MONTH[year_month[1]])
        set1 = (random.randint(self.MIN_DATE.year,self.MAX_DATE.year - 1),random.randint(1,12))
        set2 = (random.randint(self.MIN_DATE.year,self.MAX_DATE.year - 1),(set1[1]+2)%12 + 1)
        self.date_set = (datetime.datetime(set1[0],set1[1],calc_leap_day(set1),tzinfo=pytz.utc),datetime.datetime(set2[0],set2[1],calc_leap_day(set2),tzinfo=pytz.utc))
        # date difference has to be in between range 
        while abs(self.date_set[0].timestamp() - self.date_set[1].timestamp()) < (self.MIN_RANGE *86400) or abs(self.date_set[0].timestamp() - self.date_set[1].timestamp()) > (self.MAX_RANGE * 86400):
            n_list= (set1[0],random.randint(1,12))
            self.date_set = (datetime.datetime(set1[0],set1[1],calc_leap_day(set1),tzinfo=pytz.utc),datetime.datetime(n_list[0],n_list[1],calc_leap_day(n_list),tzinfo=pytz.utc))
        if self.date_set[0] > datetime.datetime.now().replace(tzinfo=pytz.utc):
            self.date_set = (datetime.datetime.now().replace(month = 1, day=1,tzinfo=pytz.utc),self.date_set[1])
        if self.date_set[1] > datetime.datetime.now().replace(tzinfo=pytz.utc):
            self.date_set = (self.date_set[0],datetime.datetime.now().replace(month=3,day=int(datetime.datetime.today().strftime('%d')), tzinfo=pytz.utc))
        self.date_set=self._reorder_dates(self.date_set[0].date(),self.date_set[1].date())
        return self.date_set
    def get_date_difference(self,date1=None,date2=None):
        if date1 is None:
            return (self.date_set[0] - self.date_set[1]).days
        else:
            return (date2 - date1).days
    def get_data(self):
        return self.data
    # Twitter API Web Scraper for data on specific stocks
    def get_recent_news(self,query):
        response = requests.post(self.search_url,json=query, headers=self.headers)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()
# g = Gather()
# g.set_indicator("AMD")
# g.set_data_from_range(datetime.datetime(year=2020,month=9,day=9), datetime.datetime(year=2021,month=10,day=9))
