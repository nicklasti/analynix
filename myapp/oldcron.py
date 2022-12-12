
# Periodic Caching System:
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
# Creates an empty dictionary (no shit)
def get_stock_dic(ind):
    industry = ind
    foverview = Valuation()
    filters_dict = {'Industry': industry}
    foverview.set_filter(filters_dict=filters_dict)
    df = foverview.screener_view()
    time.sleep(2)
    ticker_list = df['Ticker']
    for stock_ticker in ticker_list:
        if stock_ticker != 'MOHO' and stock_ticker != 'PFHC' and stock_ticker != 'USWS' and stock_ticker != 'SRLP' and stock_ticker != 'STON':
            stock = None
            while stock == None:
                try:
                    stock = finvizfinance(stock_ticker).ticker_fundament()
                    time.sleep(2)
                except Exception:
                    time.sleep(10)
        # Stores the basic stock data as a variable
            sector = stock['Sector']
            # Gets the sector
            ticker = stock_ticker
            # Gets the ticker
            company_name = stock['Company']
            # Gets the company name
            beta = stock['Beta']
            beta = fix_dashes(beta)
            book_sh = (stock['Book/sh'])
            if book_sh == '-':
                book_sh = str(0)
                bvps = 0
            else:
                bvps = float(book_sh)


            shares_outstanding = stock['Shs Outstand']
            if shares_outstanding == '-':
                shares_outstanding=0
            else:
                shares_outstanding = float(stock['Shs Outstand'][:-1]) * float(DOLLAR_MAPPING[stock['Shs Outstand'][-1]])
            
            book_value = bvps * shares_outstanding

            pb = stock['P/B']
            pb = fix_dashes(pb)
            pb_float = pb
            if pb == 0:
                pb = 'N/A'
            ps = stock['P/S']
            ps = fix_dashes(ps)
            ps_float = ps
            if ps == 0:
                ps = 'N/A'
            pe = stock['P/E']
            pe = fix_dashes(pe)
            pe_float=pe
            if pe == 0:
                pe = 'N/A'
            fwdpe = stock['Forward P/E']
            fwdpe = fix_dashes(fwdpe)
            fwdpe_float = fwdpe
            if fwdpe == 0:
                fwdpe = 'N/A'
            eps = stock['EPS (ttm)']
            eps = fix_dashes(eps)
            eps_float = eps
            if fwdpe == 0:
                fwdpe = 'N/A'
            mkt_cap_short = stock['Market Cap']
            if mkt_cap_short == '-':
                mkt_cap_short = str(0)
                mkt_cap = 0
            else:
                mkt_cap = float(mkt_cap_short[:-1]) * float(DOLLAR_MAPPING[mkt_cap_short[-1]])
            #gets mkt cap
            revenue_short = stock['Sales']
            if revenue_short == '-':
                revenue_short = str(0)
                revenue = 0
            else:
                revenue = float(revenue_short[:-1]) * float(DOLLAR_MAPPING[revenue_short[-1]])
            # gets the sales
            profit_short = stock['Income']
            if profit_short == '-':
                profit = 0
                profit_short = '0'
            else:
                profit = float(profit_short[:-1]) * float(DOLLAR_MAPPING[profit_short[-1]])
            # gets the net income
            profit_margin = stock['Profit Margin']
            if profit_margin == '-':
                profit_margin = str(0)
                profit_margin_float = 0
            else:
                profit_margin_float = float(profit_margin[:-1])/100
            if profit == 0:
                profit_margin='N/A'
            # gets the PM
            rev_growth = stock['Sales Q/Q']
            if rev_growth == '-':
                rev_growth = str(0)
                rev_growth_float = 0
            else:
                rev_growth_float = float(rev_growth[:-1])/100
            if revenue == 0:
                rev_growth == 'N/A'
            # gets rev growth
            avg_volume = stock['Avg Volume']

            if avg_volume == '-':
                avg_volume = str(0)
                avg_volume_float=0
            else:
                avg_volume_float=float(avg_volume[:-1]) * float(DOLLAR_MAPPING[avg_volume[-1]])

            print(stock)

            shares_float = stock['Shs Float']

            if shares_float == '-':
                shares_float = str(0)
                shares_float_float=0
            else:
                shares_float_float=float(shares_float[:-1]) * float(DOLLAR_MAPPING[shares_float[-1]])
            
            short_float = stock['Short Float / Ratio']

            short_float = short_float.split('/')[0].strip()

            if short_float == '-':
                short_float = str(0)
                short_float_float = 0
            else:
                short_float_float = float(short_float[:-1])/100

            if short_float == '-':
                short_float = str(0)

            if book_value == '-':
                book_value = 0

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

            # gets revenue growth
            stock_dic[ticker] = {'company_name': company_name, 'ticker': ticker, 'industry': industry, 'beta': beta, 'mkt_cap' : mkt_cap,'mkt_cap_short': mkt_cap_short, 'revenue': revenue, 'revenue_short':revenue_short,'profit': profit, 'profit_short':profit_short, 'profit_margin':profit_margin, 'sector': sector,'rev_growth': rev_growth, 'pe': pe,'fwdpe':fwdpe, 'profit_margin_float': profit_margin_float,'rev_growth_float':rev_growth_float,'ps':ps,'eps':eps,'pb':pb,'avg_volume':avg_volume,'shares_float':shares_float,'short_float':short_float,'book_value':book_value,'bvps':bvps,'avg_volume_float':avg_volume_float,'shares_float_float':shares_float_float,'short_float_float':short_float_float,'prices':prices,'dates':dates,'pb_float':pb_float,'ps_float':ps_float,'pe_float':pe_float,'fwdpe_float':fwdpe_float,'eps_float':eps_float}
            print(stock_dic[ticker])
        else:
            continue
    return stock_dic
# Creates a stock dictionary for the industry

def get_industry_list():
    req = Request("https://finviz.com/groups.ashx?g=industry&v=110&#o=name",headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read().decode('utf-8')
    industries = re.findall('(?<=class="tab-link">).*?(?=</a>)',webpage,re.DOTALL)
    industries = industries[:144]
    big_industries = [industries[13],industries[17],industries[118],industries[8],industries[9],industries[37],industries[40],industries[43],industries[44],industries[62],industries[120],industries[121]]
    small_industries = []
    for industry in industries:
        if industry not in big_industries:
            small_industries.append(industry)
        small_industries = small_industries[:1]
    return small_industries
# Gets a list of all the industries

# Can run the following in the Terminal:

#  python manage.py crontab remove
#  python manage.py crontab show
#  python manage.py crontab add
#  python manage.py runserver
#  python manage.py crontab run (hash)

def get_stock_info():
    industries = get_industry_list()
    print(industries)
    industries = industries
    print(industries)
    for industry in industries:
        get_stock_dic(industry)
        for stock in stock_dic:
            if stock_dic[stock]['ticker'] != 'PFHC':
                StockInfo.objects.update_or_create(
                    name = stock_dic[stock]['ticker'],
                    industry = stock_dic[stock]['industry'],
                    sector = stock_dic[stock]['sector'],
                    company_name = stock_dic[stock]['company_name'],
                    beta = stock_dic[stock]['beta'],
                    pb=stock_dic[stock]['pb'],
                    ps=stock_dic[stock]['ps'],
                    pe=stock_dic[stock]['pe'],
                    fwdpe=stock_dic[stock]['fwdpe'],
                    eps=stock_dic[stock]['eps'],
                    mkt_cap_short=stock_dic[stock]['mkt_cap_short'],
                    mkt_cap=stock_dic[stock]['mkt_cap'],
                    revenue_short=stock_dic[stock]['revenue_short'],
                    revenue=stock_dic[stock]['revenue'],
                    profit_short=stock_dic[stock]['profit_short'],
                    profit=stock_dic[stock]['profit'],
                    profit_margin=stock_dic[stock]['profit_margin'],
                    profit_margin_float=stock_dic[stock]['profit_margin_float'],
                    rev_growth=stock_dic[stock]['rev_growth'],
                    rev_growth_float=stock_dic[stock]['rev_growth_float'],
                    avg_volume=stock_dic[stock]['avg_volume'],
                    shares_float=stock_dic[stock]['shares_float'],
                    short_float=stock_dic[stock]['short_float'],
                    book_value=stock_dic[stock]['book_value'],
                    bvps=stock_dic[stock]['bvps'],
                    avg_volume_float=stock_dic[stock]['avg_volume_float'],
                    shares_float_float=stock_dic[stock]['shares_float_float'],
                    short_float_float=stock_dic[stock]['short_float_float'],
                    pb_float=stock_dic[stock]['pb_float'],
                    ps_float=stock_dic[stock]['ps_float'],
                    pe_float=stock_dic[stock]['pe_float'],
                    fwdpe_float=stock_dic[stock]['fwdpe_float'],
                    eps_float=stock_dic[stock]['eps_float'],
                    prices = {'prices':stock_dic[stock]['prices']},
                    dates = {'dates':stock_dic[stock]['dates']}

                    )
                print('done saving'+stock_dic[stock]['ticker'])
            else:
                continue
# Gets all data on all stocks and stores it

def get_bigindustry_list():
    req = Request("https://finviz.com/groups.ashx?g=industry&v=110&#o=name",headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read().decode('utf-8')
    industries = re.findall('(?<=class="tab-link">).*?(?=</a>)',webpage,re.DOTALL)
    industries = industries[:144]
    big_industries = [industries[120],industries[121],industries[8],industries[9],industries[37],industries[40],industries[43],industries[44],industries[62],industries[13],industries[17],industries[118]]
    big_industries = big_industries
    #should start w electronic components end with life insurance when printed
    print(big_industries)
    return big_industries

big_stock_dic={}

big_ticka_list = []

def get_big_stock_dic():
    bigindlist = get_bigindustry_list()
    newbigindlist=[]
    for i in bigindlist:
        i = i.lower()
        i = i.replace(" ", "")
        i = i.replace("&","")
        i = i.replace("-", "")
        newbigindlist.append(i)

    rlist = [
                '','21','41','61','81','101','121','141','161','181','201','221','241','261','281','301','321','341','361','381','401','421','441','461','481','501','521','541','561','581','601','621','641','661','681','701','721','741','761','781'
            ]

    def add_tickers_to_list(tickalist):
        try:
            for ticker in tickalist:
                if ticker not in big_ticka_list:
                    print(ticker)
                    big_ticka_list.append(ticker)
                else: continue
        except:
            pass

    def get_tickers_from_page(i,page):
        reqdef1 = Request('https://finviz.com/screener.ashx?f=ind_'+i+'&r='+page, headers={'User-Agent': 'Mozilla/5.0'})
        urlsite = urlopen(reqdef1).read().decode('utf-8')
        tickalist = re.findall('(?<=class="screener-link-primary">).*?(?=</a>)',urlsite, re.DOTALL)
        add_tickers_to_list(tickalist)
    

    for i in newbigindlist:
        for page in rlist:
            try:
                get_tickers_from_page(i,page)
                time.sleep(.3)
            except Exception:
                time.sleep(3)
                print("problem with adding tickers from a certain page from"+i)
    for stock_ticker in big_ticka_list:
        if stock_ticker != 'ADD' and stock_ticker != 'BENE':
            stock = None
            while stock == None:
                try:
                    stock = finvizfinance(stock_ticker).ticker_fundament()
                    time.sleep(.3)
                except Exception:
                    time.sleep(5)
                    print("problem with getting the actual ticker info for"+stock_ticker)
            # Stores the basic stock data as a variable
            industry = stock['Industry']
            sector = stock['Sector']
            # Gets the sector
            ticker = stock_ticker
            # Gets the ticker
            company_name = stock['Company']
            print(company_name)
            # Gets the company name
            beta = stock['Beta']
            beta = fix_dashes(beta)
            book_sh = (stock['Book/sh'])
            if book_sh == '-':
                book_sh = str(0)
                bvps = 0
            else:
                bvps = float(book_sh)


            shares_outstanding = stock['Shs Outstand']
            if shares_outstanding == '-':
                shares_outstanding=0
            else:
                shares_outstanding = float(stock['Shs Outstand'][:-1]) * float(DOLLAR_MAPPING[stock['Shs Outstand'][-1]])
            
            book_value = bvps * shares_outstanding

            pb = stock['P/B']
            pb = fix_dashes(pb)
            pb_float = pb
            if pb == 0:
                pb = 'N/A'
            ps = stock['P/S']
            ps = fix_dashes(ps)
            ps_float = ps
            if ps == 0:
                ps = 'N/A'
            pe = stock['P/E']
            pe = fix_dashes(pe)
            pe_float=pe
            if pe == 0:
                pe = 'N/A'
            fwdpe = stock['Forward P/E']
            fwdpe = fix_dashes(fwdpe)
            fwdpe_float = fwdpe
            if fwdpe == 0:
                fwdpe = 'N/A'
            eps = stock['EPS (ttm)']
            eps = fix_dashes(eps)
            eps_float = eps
            if fwdpe == 0:
                fwdpe = 'N/A'
            mkt_cap_short = stock['Market Cap']
            if mkt_cap_short == '-':
                mkt_cap_short = str(0)
                mkt_cap = 0
            else:
                mkt_cap = float(mkt_cap_short[:-1]) * float(DOLLAR_MAPPING[mkt_cap_short[-1]])
            #gets mkt cap
            revenue_short = stock['Sales']
            if revenue_short == '-':
                revenue_short = str(0)
                revenue = 0
            else:
                revenue = float(revenue_short[:-1]) * float(DOLLAR_MAPPING[revenue_short[-1]])
            # gets the sales
            profit_short = stock['Income']
            if profit_short == '-':
                profit = 0
                profit_short = '0'
            else:
                profit = float(profit_short[:-1]) * float(DOLLAR_MAPPING[profit_short[-1]])
            # gets the net income
            profit_margin = stock['Profit Margin']
            if profit_margin == '-':
                profit_margin = str(0)
                profit_margin_float = 0
            else:
                profit_margin_float = float(profit_margin[:-1])/100
            # gets the PM
            rev_growth = stock['Sales Q/Q']
            if rev_growth == '-':
                rev_growth = str(0)
                rev_growth_float = 0
            else:
                rev_growth_float = float(rev_growth[:-1])/100
            # gets rev growth
            avg_volume = stock['Avg Volume']

            if avg_volume == '-':
                avg_volume = str(0)
                avg_volume_float=0
            else:
                avg_volume_float=float(avg_volume[:-1]) * float(DOLLAR_MAPPING[avg_volume[-1]])

            shares_float = stock['Shs Float']

            if shares_float == '-':
                shares_float = str(0)
                shares_float_float=0
            else:
                shares_float_float=float(shares_float[:-1]) * float(DOLLAR_MAPPING[shares_float[-1]])
            
            short_float = stock['Short Float / Ratio']

            short_float = short_float.split('/')[0].strip()

            if short_float == '-':
                short_float = str(0)
                short_float_float = 0
            else:
                short_float_float = float(short_float[:-1])/100

            pryce = list()
            while len(pryce) == 0:
                try:
                    df1 = pdr.data.get_data_yahoo(stock_ticker, start='1970-1-1', end=today)
                    time.sleep(.3)
                    pryce = df1['Close']
                except Exception:
                    time.sleep(5)
            pryce = pryce.values.tolist()
            deight1 = df1['Close']
            deight = deight1.index.tolist()
            deight = [datetime.strftime(d, '%Y-%m-%d') for d in deight]
            date_max = deight[0]
            pryce = list()
            while len(pryce) == 0:
                try:
                    df1 = pdr.data.get_data_yahoo(stock_ticker, start=date_max, end=today)
                    time.sleep(.3)
                    pryce = df1['Close']
                except Exception:
                    time.sleep(5)
            prices = pryce.values.tolist()
            deight1 = df1['Close']
            deight = deight1.index.tolist()
            dates = [datetime.strftime(d, '%Y-%m-%d') for d in deight]
            # Gets Prices and Corresponding Dates

            # gets revenue growth
            big_stock_dic[ticker] = {'company_name': company_name, 'ticker': ticker, 'industry': industry, 'beta': beta, 'mkt_cap' : mkt_cap,'mkt_cap_short': mkt_cap_short, 'revenue': revenue, 'revenue_short':revenue_short,'profit': profit, 'profit_short':profit_short, 'profit_margin':profit_margin, 'sector': sector,'rev_growth': rev_growth, 'pe': pe,'fwdpe':fwdpe, 'profit_margin_float': profit_margin_float,'rev_growth_float':rev_growth_float,'ps':ps,'eps':eps,'pb':pb,'avg_volume':avg_volume,'shares_float':shares_float,'short_float':short_float,'book_value':book_value,'bvps':bvps,'avg_volume_float':avg_volume_float,'shares_float_float':shares_float_float,'short_float_float':short_float_float,'prices':prices,'dates':dates,'ps_float':ps_float,'pe_float':pe_float,'pb_float':pb_float,'eps_float':eps_float,'fwdpe_float':fwdpe_float}
            print('added',ticker,'in the dictionary')
    return big_stock_dic

def get_big_stock_info():
    get_big_stock_dic()
    for stock in big_stock_dic:
        print ('saving:',big_stock_dic[stock]['ticker'])
        StockInfo.objects.update_or_create(
            name = big_stock_dic[stock]['ticker'],
            industry = big_stock_dic[stock]['industry'],
            sector = big_stock_dic[stock]['sector'],
            company_name = big_stock_dic[stock]['company_name'],
            beta = big_stock_dic[stock]['beta'],
            pb=big_stock_dic[stock]['pb'],
            ps=big_stock_dic[stock]['ps'],
            pe=big_stock_dic[stock]['pe'],
            fwdpe=big_stock_dic[stock]['fwdpe'],
            eps=big_stock_dic[stock]['eps'],
            pb_float=big_stock_dic[stock]['pb_float'],
            ps_float=big_stock_dic[stock]['ps_float'],
            pe_float=big_stock_dic[stock]['pe_float'],
            fwdpe_float=big_stock_dic[stock]['fwdpe_float'],
            eps_float=big_stock_dic[stock]['eps_float'],
            mkt_cap_short=big_stock_dic[stock]['mkt_cap_short'],
            mkt_cap=big_stock_dic[stock]['mkt_cap'],
            revenue_short=big_stock_dic[stock]['revenue_short'],
            revenue=big_stock_dic[stock]['revenue'],
            profit_short=big_stock_dic[stock]['profit_short'],
            profit=big_stock_dic[stock]['profit'],
            profit_margin=big_stock_dic[stock]['profit_margin'],
            profit_margin_float=big_stock_dic[stock]['profit_margin_float'],
            rev_growth=big_stock_dic[stock]['rev_growth'],
            rev_growth_float=big_stock_dic[stock]['rev_growth_float'],
            avg_volume=big_stock_dic[stock]['avg_volume'],
            shares_float=big_stock_dic[stock]['shares_float'],
            short_float=big_stock_dic[stock]['short_float'],
            book_value=big_stock_dic[stock]['book_value'],
            bvps=big_stock_dic[stock]['bvps'],
            avg_volume_float=big_stock_dic[stock]['avg_volume_float'],
            shares_float_float=big_stock_dic[stock]['shares_float_float'],
            short_float_float=big_stock_dic[stock]['short_float_float'],
            prices = {'prices':big_stock_dic[stock]['prices']},
            dates = {'dates':big_stock_dic[stock]['dates']}
            )

def sql_queries():
    avg_list = StockInfo.objects.values()
    for x in avg_list:
        ticker = x['name']
        industry = x['industry']
        avg_volume_float = x['avg_volume_float']
        shares_float_float =x['shares_float_float']
        short_float_float =x['short_float_float']
        revenue = int(x['revenue'])
        profit = int(x['profit'])
        mkt_cap = int(x['mkt_cap'])
        rev_growth_float = float(x['rev_growth_float'])
        profit_margin_float = float(x['profit_margin_float'])
        profit_margin = x['profit_margin']
        pe_float= x['pe_float']
        pe = x['pe']
        ps_float = x['ps_float']
        ps = x['ps']
        eps_float = x['eps_float']
        eps = x['eps']
        fwdpe_float = x['fwdpe_float']
        fwdpe = x['fwdpe']
        pb_float = x['pb_float']
        pb = x['pb']
        book_value = x['book_value']

        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(pe_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_pe = cursor.fetchall()
        for x in avg_pe:
            avg_pe = float(x[1])

        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(ps_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_ps = cursor.fetchall()
        for x in avg_ps:
            avg_ps = float(x[1])

        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(pb_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_pb = cursor.fetchall()
        for x in avg_pb:
            avg_pb = float(x[1])

        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(eps_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_eps = cursor.fetchall()
        for x in avg_eps:
            avg_eps = float(x[1])

        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(fwdpe_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_fwdpe = cursor.fetchall()
        for x in avg_fwdpe:
            avg_fwdpe = float(x[1])

        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(mkt_cap) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_mkt_cap = cursor.fetchall()
        for x in avg_mkt_cap:
            avg_mkt_cap = x[1]

        cursor = connection.cursor()
        cursor.execute('SELECT name, COUNT(revenue) FROM myapp_stockinfo WHERE industry = %s',[industry])
        numba_o_stocks_in_industry = cursor.fetchall()
        for x in numba_o_stocks_in_industry:
            numba_o_stocks_in_industry = float(x[1])

        cursor = connection.cursor()
        cursor.execute('SELECT name, SUM(mkt_cap) FROM myapp_stockinfo WHERE industry = %s',[industry])
        ind_size = cursor.fetchall()
        for x in ind_size:
            ind_size = float(x[1])    

        try:
            dtc = round(((short_float_float * shares_float_float)/avg_volume_float),2)
        except Exception:
            dtc = 0

        revenue_short = human_format(revenue)

        profit_short = human_format(profit)

        mkt_share = '{:.2%}'.format(mkt_cap/ind_size)

        mkt_share_float = mkt_cap/ind_size

        ind_size = human_format(ind_size)

        avg_mkt_cap = human_format(avg_mkt_cap)
        


        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(revenue) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_rev = cursor.fetchall()
        for x in avg_rev:
            avg_rev = human_format(x[1])
            avg_rev_float = x[1]
        
        how_much_above_or_below = revenue - avg_rev_float

        cursor = connection.cursor()
        cursor.execute('SELECT AVG(revenue*revenue) - AVG(revenue)*AVG(revenue) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        top_var = cursor.fetchall()
        for x in top_var:
            top_var = x[0]
        var = top_var/numba_o_stocks_in_industry
        stdev = math.sqrt(var)
        how_many_stdevs= how_much_above_or_below/stdev
        if how_many_stdevs >= 5:
            grade = 'A+'
        elif how_many_stdevs >= 4:
            grade = 'A'
        elif how_many_stdevs >= 3.8:
            grade = 'A-'
        elif how_many_stdevs >= 3:
            grade = 'B+'
        elif how_many_stdevs >= 1:
            grade = 'B'
        elif how_many_stdevs >= 0:
            grade = 'B-'
        elif how_many_stdevs >= -1:
            grade = 'C+'
        elif how_many_stdevs >= -2:
            grade = 'C'
        elif how_many_stdevs >= -3.:
            grade = 'C-'
        elif how_many_stdevs >= -3.4:
            grade = 'D+'
        elif how_many_stdevs >= -3.7:
            grade = 'D'
        elif how_many_stdevs >= -3.8:
            grade = 'D-'
        elif how_many_stdevs >= -3.9:
            grade = 'F'
        elif how_many_stdevs < -3.9:
            grade = 'F-'
        
        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(profit) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_profit = cursor.fetchall()
        for x in avg_profit:
            avg_profit = human_format(x[1])
            avg_profit_float = x[1]

        profit_dif = profit - avg_profit_float

        cursor = connection.cursor()
        cursor.execute('SELECT AVG(profit*profit) - AVG(profit)*AVG(profit) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        profit_top_var = cursor.fetchall()
        for x in profit_top_var:
            profit_top_var = x[0]
        profit_var = profit_top_var/numba_o_stocks_in_industry
        profit_stdev = math.sqrt(profit_var)
        profit_stdevs = profit_dif/profit_stdev
        if profit_stdevs >= 5:
            profit_grade = 'A+'
        elif profit_stdevs >= 4:
            profit_grade = 'A'
        elif profit_stdevs >= 3.8:
            profit_grade = 'A-'
        elif profit_stdevs >= 3:
            profit_grade = 'B+'
        elif profit_stdevs >= 1:
            profit_grade = 'B'
        elif profit_stdevs >= 0:
            profit_grade = 'B-'
        elif profit_stdevs >= -1:
            profit_grade = 'C+'
        elif profit_stdevs >= -2:
            profit_grade = 'C'
        elif profit_stdevs >= -3.:
            profit_grade = 'C-'
        elif profit_stdevs >= -3.4:
            profit_grade = 'D+'
        elif profit_stdevs >= -3.7:
            profit_grade = 'D'
        elif profit_stdevs >= -3.8:
            profit_grade = 'D-'
        elif profit_stdevs >= -3.9:
            profit_grade = 'F'
        elif profit_stdevs < -3.9:
            profit_grade = 'F-'
            
        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(rev_growth_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_rev_growth = cursor.fetchall()
        for x in avg_rev_growth:
            avg_rev_growth = '{:.2%}'.format(x[1])
            avg_rev_growth_float = x[1]

        rev_growth_dif = rev_growth_float - avg_rev_growth_float

        cursor = connection.cursor()
        cursor.execute('SELECT AVG(rev_growth_float*rev_growth_float) - AVG(rev_growth_float)*AVG(rev_growth_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        rev_growth_top_var = cursor.fetchall()
        for x in rev_growth_top_var:
            rev_growth_top_var = x[0]
        rev_growth_var = rev_growth_top_var/numba_o_stocks_in_industry
        rev_growth_stdev = math.sqrt(rev_growth_var)
        rev_growth_stdevs = rev_growth_dif/rev_growth_stdev
        if revenue == 'N/A':
            rev_growth_grade = 'N/A'
        elif rev_growth_stdevs >= 5:
            rev_growth_grade = 'A+'
        elif rev_growth_stdevs >= 4:
            rev_growth_grade = 'A'
        elif rev_growth_stdevs >= 3.8:
            rev_growth_grade = 'A-'
        elif rev_growth_stdevs >= 3:
            rev_growth_grade = 'B+'
        elif rev_growth_stdevs >= 1:
            rev_growth_grade = 'B'
        elif rev_growth_stdevs >= 0:
            rev_growth_grade = 'B-'
        elif rev_growth_stdevs >= -1:
            rev_growth_grade = 'C+'
        elif rev_growth_stdevs >= -2:
            rev_growth_grade = 'C'
        elif rev_growth_stdevs >= -3.:
            rev_growth_grade = 'C-'
        elif rev_growth_stdevs >= -3.4:
            rev_growth_grade = 'D+'
        elif rev_growth_stdevs >= -3.7:
            rev_growth_grade = 'D'
        elif rev_growth_stdevs >= -3.8:
            rev_growth_grade = 'D-'
        elif rev_growth_stdevs >= -3.9:
            rev_growth_grade = 'F'
        elif rev_growth_stdevs < -3.9:
            rev_growth_grade = 'F-'

        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(profit_margin_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_profit_margin = cursor.fetchall()
        for x in avg_profit_margin:
            avg_profit_margin = '{:.2%}'.format(x[1])
            avg_profit_margin_float = x[1]
        
        profit_margin_dif = profit_margin_float - avg_profit_margin_float

        cursor = connection.cursor()
        cursor.execute('SELECT AVG(profit_margin_float*profit_margin_float) - AVG(profit_margin_float)*AVG(profit_margin_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        profit_margin_top_var = cursor.fetchall()
        for x in profit_margin_top_var:
            profit_margin_top_var = x[0]
        profit_margin_var = profit_margin_top_var/numba_o_stocks_in_industry
        profit_margin_stdev = math.sqrt(profit_margin_var)
        profit_margin_stdevs = profit_margin_dif/profit_margin_stdev
        if profit_margin == "N/A":
            profit_margin_grade = 'N/A'
        elif profit_margin_stdevs >= 5:
            profit_margin_grade = 'A+'
        elif profit_margin_stdevs >= 4:
            profit_margin_grade = 'A'
        elif profit_margin_stdevs >= 3.8:
            profit_margin_grade = 'A-'
        elif profit_margin_stdevs >= 3:
            profit_margin_grade = 'B+'
        elif profit_margin_stdevs >= 1:
            profit_margin_grade = 'B'
        elif profit_margin_stdevs >= 0:
            profit_margin_grade = 'B-'
        elif profit_margin_stdevs >= -1:
            profit_margin_grade = 'C+'
        elif profit_margin_stdevs >= -2:
            profit_margin_grade = 'C'
        elif profit_margin_stdevs >= -3.:
            profit_margin_grade = 'C-'
        elif profit_margin_stdevs >= -3.4:
            profit_margin_grade = 'D+'
        elif profit_margin_stdevs >= -3.7:
            profit_margin_grade = 'D'
        elif profit_margin_stdevs >= -3.8:
            profit_margin_grade = 'D-'
        elif profit_margin_stdevs >= -3.9:
            profit_margin_grade = 'F'
        elif profit_margin_stdevs < -3.9:
            profit_margin_grade = 'F-'
        pe_dif = avg_pe - pe_float
        cursor = connection.cursor()
        cursor.execute('SELECT AVG(pe_float*pe_float) - AVG(pe_float)*AVG(pe_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        pe_top_var = cursor.fetchall()
        for x in pe_top_var:
            pe_top_var = x[0]
        pe_var = pe_top_var/numba_o_stocks_in_industry
        pe_stdev = math.sqrt(pe_var)
        pe_stdevs = pe_dif/pe_stdev
        if pe == 'N/A':
            pe_grade = 'N/A'
        elif pe_stdevs >= 5:
            pe_grade = 'A+'
        elif pe_stdevs >= 4:
            pe_grade = 'A'
        elif pe_stdevs >= 3.8:
            pe_grade = 'A-'
        elif pe_stdevs >= 3:
            pe_grade = 'B+'
        elif pe_stdevs >= 1:
            pe_grade = 'B'
        elif pe_stdevs >= 0:
            pe_grade = 'B-'
        elif pe_stdevs >= -1:
            pe_grade = 'C+'
        elif pe_stdevs >= -2:
            pe_grade = 'C'
        elif pe_stdevs >= -3.:
            pe_grade = 'C-'
        elif pe_stdevs >= -3.4:
            pe_grade = 'D+'
        elif pe_stdevs >= -3.7:
            pe_grade = 'D'
        elif pe_stdevs >= -3.8:
            pe_grade = 'D-'
        elif pe_stdevs >= -3.9:
            pe_grade = 'F'
        elif pe_stdevs < -3.9:
            pe_grade = 'F-'
        
        ps_dif = avg_ps - ps_float
        
        cursor = connection.cursor()
        cursor.execute('SELECT AVG(ps*ps) - AVG(ps)*AVG(ps) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        ps_top_var = cursor.fetchall()
        for x in ps_top_var:
            ps_top_var = x[0]
        ps_var = ps_top_var/numba_o_stocks_in_industry
        ps_stdev = math.sqrt(ps_var)
        ps_stdevs = ps_dif/ps_stdev
        
        if ps == 'N/A':
            pb_grade = 'N/A'
        elif ps_stdevs >= 5:
            ps_grade = 'A+'
        elif ps_stdevs >= 4:
            ps_grade = 'A'
        elif ps_stdevs >= 3.8:
            ps_grade = 'A-'
        elif ps_stdevs >= 3:
            ps_grade = 'B+'
        elif ps_stdevs >= 1:
            ps_grade = 'B'
        elif ps_stdevs >= 0:
            ps_grade = 'B-'
        elif ps_stdevs >= -1:
            ps_grade = 'C+'
        elif ps_stdevs >= -2:
            ps_grade = 'C'
        elif ps_stdevs >= -3.:
            ps_grade = 'C-'
        elif ps_stdevs >= -3.4:
            ps_grade = 'D+'
        elif ps_stdevs >= -3.7:
            ps_grade = 'D'
        elif ps_stdevs >= -3.8:
            ps_grade = 'D-'
        elif ps_stdevs >= -3.9:
            ps_grade = 'F'
        elif ps_stdevs < -3.9:
            ps_grade = 'F-'
        
        eps_dif = avg_eps - eps_float
        
        cursor = connection.cursor()
        cursor.execute('SELECT AVG(eps*eps) - AVG(eps)*AVG(eps) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        eps_top_var = cursor.fetchall()
        for x in eps_top_var:
            eps_top_var = x[0]
        eps_var = eps_top_var/numba_o_stocks_in_industry
        eps_stdev = math.sqrt(eps_var)
        eps_stdevs = eps_dif/eps_stdev
        
        if eps == 'N/A':
            eps_grade = 'N/A'
        elif eps_stdevs >= 5:
            eps_grade = 'A+'
        elif eps_stdevs >= 4:
            eps_grade = 'A'
        elif eps_stdevs >= 3.8:
            eps_grade = 'A-'
        elif eps_stdevs >= 3:
            eps_grade = 'B+'
        elif eps_stdevs >= 1:
            eps_grade = 'B'
        elif eps_stdevs >= 0:
            eps_grade = 'B-'
        elif eps_stdevs >= -1:
            eps_grade = 'C+'
        elif eps_stdevs >= -2:
            eps_grade = 'C'
        elif eps_stdevs >= -3.:
            eps_grade = 'C-'
        elif eps_stdevs >= -3.4:
            eps_grade = 'D+'
        elif eps_stdevs >= -3.7:
            eps_grade = 'D'
        elif eps_stdevs >= -3.8:
            eps_grade = 'D-'
        elif eps_stdevs >= -3.9:
            eps_grade = 'F'
        elif eps_stdevs < -3.9:
            eps_grade = 'F-'
        
        fwdpe_dif = avg_fwdpe - fwdpe_float
        
        cursor = connection.cursor()
        cursor.execute('SELECT AVG(fwdpe*fwdpe) - AVG(fwdpe)*AVG(fwdpe) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        fwdpe_top_var = cursor.fetchall()
        for x in fwdpe_top_var:
            fwdpe_top_var = x[0]
        fwdpe_var = fwdpe_top_var/numba_o_stocks_in_industry
        fwdpe_stdev = math.sqrt(fwdpe_var)
        fwdpe_stdevs = fwdpe_dif/fwdpe_stdev
        
        if fwdpe == 'N/A':
            fwdpe_grade = 'N/A'
        elif fwdpe_stdevs >= 5:
            fwdpe_grade = 'A+'
        elif fwdpe_stdevs >= 4:
            fwdpe_grade = 'A'
        elif fwdpe_stdevs >= 3.8:
            fwdpe_grade = 'A-'
        elif fwdpe_stdevs >= 3:
            fwdpe_grade = 'B+'
        elif fwdpe_stdevs >= 1:
            fwdpe_grade = 'B'
        elif fwdpe_stdevs >= 0:
            fwdpe_grade = 'B-'
        elif fwdpe_stdevs >= -1:
            fwdpe_grade = 'C+'
        elif fwdpe_stdevs >= -2:
            fwdpe_grade = 'C'
        elif fwdpe_stdevs >= -3.:
            fwdpe_grade = 'C-'
        elif fwdpe_stdevs >= -3.4:
            fwdpe_grade = 'D+'
        elif fwdpe_stdevs >= -3.7:
            fwdpe_grade = 'D'
        elif fwdpe_stdevs >= -3.8:
            fwdpe_grade = 'D-'
        elif fwdpe_stdevs >= -3.9:
            fwdpe_grade = 'F'
        elif fwdpe_stdevs < -3.9:
            fwdpe_grade = 'F-'
        
        pb_dif = avg_pb - pb_float
        
        cursor = connection.cursor()
        cursor.execute('SELECT AVG(pb*pb) - AVG(pb)*AVG(pb) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        pb_top_var = cursor.fetchall()
        for x in pb_top_var:
            pb_top_var = x[0]
        pb_var = pb_top_var/numba_o_stocks_in_industry
        pb_stdev = math.sqrt(pb_var)
        pb_stdevs = pb_dif/pb_stdev
        
        if pb == 'N/A':
            pb_grade = 'N/A'
        elif pb_stdevs >= 5:
            pb_grade = 'A+'
        elif pb_stdevs >= 4:
            pb_grade = 'A'
        elif pb_stdevs >= 3.8:
            pb_grade = 'A-'
        elif pb_stdevs >= 3:
            pb_grade = 'B+'
        elif pb_stdevs >= 1:
            pb_grade = 'B'
        elif pb_stdevs >= 0:
            pb_grade = 'B-'
        elif pb_stdevs >= -1:
            pb_grade = 'C+'
        elif pb_stdevs >= -2:
            pb_grade = 'C'
        elif pb_stdevs >= -3.:
            pb_grade = 'C-'
        elif pb_stdevs >= -3.4:
            pb_grade = 'D+'
        elif pb_stdevs >= -3.7:
            pb_grade = 'D'
        elif pb_stdevs >= -3.8:
            pb_grade = 'D-'
        elif pb_stdevs >= -3.9:
            pb_grade = 'F'
        elif pb_stdevs < -3.9:
            pb_grade = 'F-'

        if book_value == '-':
            book_value = 0
        else:
            book_value = human_format(book_value)

        avg_pe = round(avg_pe,2)
        avg_eps = round(avg_eps,2)
        avg_ps = round(avg_ps,2)
        avg_pb = round(avg_pb,2)
        avg_fwdpe = round(avg_fwdpe,2)

        print('successfully calculated everything for'+ticker)

        StockInfo.objects.filter(name=ticker).update(
            avg_pe = avg_pe,
            avg_ps = avg_ps,
            avg_pb = avg_pb,
            avg_eps = avg_eps,
            avg_fwdpe = avg_fwdpe,
            avg_mkt_cap = avg_mkt_cap,
            ind_size = ind_size,
            dtc = dtc,
            revenue_short = revenue_short,
            profit_short = profit_short,
            mkt_share_float = mkt_share_float,
            mkt_share = mkt_share,
            grade = grade,
            profit_grade = profit_grade,
            rev_growth_grade = rev_growth_grade,
            profit_margin_grade = profit_margin_grade,
            pe_grade = pe_grade,
            ps_grade = ps_grade,
            pb_grade = pb_grade,
            eps_grade = eps_grade,
            fwdpe_grade = fwdpe_grade,
            avg_rev = avg_rev,
            avg_rev_growth = avg_rev_growth,
            avg_profit = avg_profit,
            avg_profit_margin = avg_profit_margin,
            book_value = book_value,
        )
        print('added'+ticker+'to the database')




#def sql_queries_grades():
#    avg_list = StockInfo.objects.values()
#    for x in avg_list:
#        ticker = x['name']
#        if x['pe_grade'] and x['ps_grade'] and x['pb_grade'] and x['eps_grade'] and x['fwdpe_grade']



def grader():
    avg_list = StockInfo.objects.values()
    for x in avg_list:
        ticker = x['name']
        grade = x['grade']
        profit_grade = x['profit_grade']
        rev_growth_grade = x['rev_growth_grade']
        profit_margin_grade = x['profit_margin_grade']
        pe_grade = x['pe_grade']
        ps_grade = x['ps_grade']
        pb_grade = x['pb_grade']
        eps_grade = x['eps_grade']
        fwdpe_grade = x['fwdpe_grade']
        GRADE_MAPPING = {
        'A+': float(7),
        'A': float(6),
        'A-': float(5),
        'B+': float(4),
        'B': float(3),
        'B-': float(2),
        'C+': float(1),
        'C': float(0),
        'C-': float(-1),
        'D+': float(-2),
        'D': float(-3),
        'D-': float(-4),
        'F+': float(-5),
        'F': float(-6),
        'F-': float(-7),
        'N/A':float(0)
        }
        overall_grade_num = GRADE_MAPPING[grade]+GRADE_MAPPING[profit_grade]+GRADE_MAPPING[rev_growth_grade]+GRADE_MAPPING[profit_margin_grade]+GRADE_MAPPING[pe_grade]+GRADE_MAPPING[ps_grade]+GRADE_MAPPING[pb_grade]+GRADE_MAPPING[eps_grade]+GRADE_MAPPING[fwdpe_grade]
        print('ticker: '+ticker+''+'grade: '+str(overall_grade_num))
        StockInfo.objects.filter(name=ticker).update(
            overall_grade_num=overall_grade_num,
        )

def grader_2():
    avg_list = StockInfo.objects.values()
    for x in avg_list:
        industry = x['industry']
        ticker = x['name']
        overall_grade_num = x['overall_grade_num']
        cursor = connection.cursor()
        cursor.execute('SELECT name, COUNT(revenue) FROM myapp_stockinfo WHERE industry = %s',[industry])
        numba_o_stocks_in_industry = cursor.fetchall()
        for x in numba_o_stocks_in_industry:
            numba_o_stocks_in_industry = float(x[1])

        cursor = connection.cursor()
        cursor.execute('SELECT name, AVG(overall_grade_num) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        avg_overall_grade_num = cursor.fetchall()
        for x in avg_overall_grade_num:
            avg_overall_grade_num = float(x[1])

        overall_grade_num_dif = avg_overall_grade_num - overall_grade_num
        
        cursor = connection.cursor()
        cursor.execute('SELECT AVG(overall_grade_num*overall_grade_num) - AVG(overall_grade_num)*AVG(overall_grade_num) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
        overall_grade_num_top_var = cursor.fetchall()
        for x in overall_grade_num_top_var:
            overall_grade_num_top_var = x[0]
        overall_grade_num_var = overall_grade_num_top_var/numba_o_stocks_in_industry
        overall_grade_num_stdev = math.sqrt(overall_grade_num_var)
        overall_grade_num_stdevs = overall_grade_num_dif/overall_grade_num_stdev
        
        if overall_grade_num == 'N/A':
            overall_grade = 'N/A'
        elif overall_grade_num_stdevs >= 5:
            overall_grade = 'A+'
        elif overall_grade_num_stdevs >= 4:
            overall_grade = 'A'
        elif overall_grade_num_stdevs >= 3.8:
            overall_grade = 'A-'
        elif overall_grade_num_stdevs >= 3:
            overall_grade = 'B+'
        elif overall_grade_num_stdevs >= 1:
            overall_grade = 'B'
        elif overall_grade_num_stdevs >= 0:
            overall_grade = 'B-'
        elif overall_grade_num_stdevs >= -1:
            overall_grade = 'C+'
        elif overall_grade_num_stdevs >= -2:
            overall_grade = 'C'
        elif overall_grade_num_stdevs >= -3.:
            overall_grade = 'C-'
        elif overall_grade_num_stdevs >= -3.4:
            overall_grade = 'D+'
        elif overall_grade_num_stdevs >= -3.7:
            overall_grade = 'D'
        elif overall_grade_num_stdevs >= -3.8:
            overall_grade = 'D-'
        elif overall_grade_num_stdevs >= -3.9:
            overall_grade = 'F'
        elif overall_grade_num_stdevs < -3.9:
            overall_grade = 'F-'

        StockInfo.objects.filter(name=ticker).update(
            overall_grade=overall_grade,
        )
        print('overall grade: '+overall_grade)

def grader_3():
    list = []
    cursor = connection.cursor()
    cursor.execute('SELECT overall_grade_num FROM myapp_stockinfo ORDER BY overall_grade_num DESC')
    best_stocks = cursor.fetchall()
    for x in best_stocks:
        best_stocks = x[0]
        list.append(best_stocks)
    
    list2 = []
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM myapp_stockinfo ORDER BY overall_grade_num DESC')
    best_stocks2 = cursor.fetchall()
    for x in best_stocks2:
        best_stocks2 = x[0]
        list2.append(best_stocks2)

    best_stocks = zip(list2[:100],list[:100])
    print(best_stocks)
    for stock in best_stocks:
        stock = stock[0]
        BestStocks.objects.update_or_create(
        name=stock,
        )
        print('added'+str(stock))

def grader_4():
    list = []
    cursor = connection.cursor()
    cursor.execute('SELECT overall_grade_num FROM myapp_stockinfo ORDER BY overall_grade_num')
    worst_stocks = cursor.fetchall()
    for x in worst_stocks:
        worst_stocks = x[0]
        list.append(worst_stocks)
    
    list2 = []
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM myapp_stockinfo ORDER BY overall_grade_num')
    worst_stocks2 = cursor.fetchall()
    for x in worst_stocks2:
        worst_stocks2 = x[0]
        list2.append(worst_stocks2)

    worst_stocks = zip(list2[:100],list[:100])
    print(worst_stocks)
    for stock in worst_stocks:
        stock = stock[0]
        WorstStocks.objects.update_or_create(
        name=stock,
        )
        print('added'+str(stock))


def stock_price_update():
    # get the start time
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

def fix_round():
    newlist = StockInfo.objects.values()
    for x in newlist[2491:]:
        if x['last_update'] != 'default':
            last_update = x['last_update']
            print(last_update)
            stock_ticker = x['name']
            #print(last_update)
            last_update = datetime.strptime(str(last_update), '%Y-%m-%d %H:%M:%S.%f')
            last_update = datetime.strftime(last_update,'%a, %b %d %I:%M %p')
            StockInfo.objects.filter(name=stock_ticker).update(last_update = last_update)
            print('updated '+str(stock_ticker))