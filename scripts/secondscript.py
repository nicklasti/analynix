import time
from myapp.models import StockInfo, BestStocks, WorstStocks
from finvizfinance.screener.valuation import Valuation
from finvizfinance.quote import finvizfinance
import pandas_datareader as pdr
import time
import datetime
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from urllib.request import Request, urlopen
import regex as re
#from django.apps import AppConfig
from finvizfinance.screener.overview import Overview
from django.conf import settings
from logging.config import IDENTIFIER
from audioop import avg
from pickle import TRUE
from cmath import nan
import pandas as pd
from pyexpat import model
from hashlib import new
from django.db import models
from unicodedata import name
from django.db import connection 
import math

today = date.today()
date_1y = datetime.now() - relativedelta(years=1)
date_2y = datetime.now() - relativedelta(years=2)
date_3y = datetime.now() - relativedelta(years=3)
date_5y = datetime.now() - relativedelta(years=5)
date_10y = datetime.now() - relativedelta(years=10)
date_250y = datetime.now() - relativedelta(years=250)
date_ytd = datetime(today.year, 1,1)

DOLLAR_MAPPING = {
    'T': float(1000000000000),
    'B': float(1000000000),
    'M': float(1000000),
    'K': float(1000),
    'e': float(0)
}
# Helps create floats from shortened long numbers

def human_format(num):
        num = float('{:.3g}'.format(float(num)))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def fix_dashes(x):
        if x == '-':
            x = 0
            return x
        else:
            x = round(float(x),2)
            return x
# Gets rid of the dash for - values and turns it into a 0
stock_dic = {}

st = time.time()
print('stock price update cronjob was ran at '+str(st))
get_values = time.time()
print('getting values now, at '+str(get_values))
list = StockInfo.objects.values()
list = list[:10]
get_values_et = time.time()
print('done getting values now, at '+str(get_values_et))
elapsed_time_get_stock_tickers = get_values_et - get_values
print('doing that took '+str(elapsed_time_get_stock_tickers)+'seconds')
for x in list:
    stock_ticker = x['name']
    print('getting prices for '+stock_ticker)
    prices_for = time.time()
    df1 = pdr.data.get_data_yahoo(stock_ticker, start='1970-1-1', end=today)
    time.sleep(.3)
    pryce = df1['Close']
    pryce = pryce.values.tolist()
    deight1 = df1['Close']
    deight = deight1.index.tolist()
    deight = [datetime.strftime(d, '%Y-%m-%d') for d in deight]
    date_max = deight[0]
    df1 = pdr.data.get_data_yahoo(stock_ticker, start=date_max, end=today)
    time.sleep(.3)
    pryce = df1['Close']
    prices = pryce.values.tolist()
    deight1 = df1['Close']
    deight = deight1.index.tolist()
    dates = [datetime.strftime(d, '%Y-%m-%d') for d in deight]
    # Gets Prices and Corresponding Dates
    stock_price = prices[-1]
    stock_price = round(float(stock_price),2)
    last_update = datetime.now()
    last_update = datetime.strftime(last_update,'%a, %b %d %I:%M %p')
    StockInfo.objects.filter(name=stock_ticker).update(
        stock_price = stock_price,
        prices = prices,
        dates = dates,
        last_update = last_update)
    prices_for_et = time.time()
    diff = prices_for_et - prices_for
    print('updated '+stock_ticker+' and that took '+str(diff)+' seconds')
et = time.time()
print('script finished running at '+et)
# get the execution time
elapsed_time = et - st
print('Total execution time for the update stock prices cronjob: ', elapsed_time, ' seconds')