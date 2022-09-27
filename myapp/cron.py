
# Periodic Caching System:
from pyexpat import model
from hashlib import new
from django.db import models
from unicodedata import name
from myapp.models import IndustryInfo, StockTest
from myapp.models import StockInfo
from finvizfinance.screener.overview import Overview
from finvizfinance.screener.valuation import Valuation
from finvizfinance.quote import finvizfinance
import math
import statistics
import time
from urllib.request import Request, urlopen
import regex as re
#from django.apps import AppConfig
from django.conf import settings
from logging.config import IDENTIFIER
from audioop import avg
from pickle import TRUE
from cmath import nan
import pandas as pd

DOLLAR_MAPPING = {
    'T': float(1000000000000),
    'B': float(1000000000),
    'M': float(1000000),
    'K': float(1000),
    'e': float(0)
}
# Helps create floats from shortened long numbers

def human_format(num):
        num = float('{:.3g}'.format(num))
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
        ps = stock['P/S']
        ps = fix_dashes(ps)
        pe = stock['P/E']
        pe = fix_dashes(pe)
        fwdpe = stock['Forward P/E']
        fwdpe = fix_dashes(fwdpe)
        eps = stock['EPS (ttm)']
        eps = fix_dashes(eps)
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
        
        short_float = stock['Short Float']

        if short_float == '-':
            short_float = str(0)
            short_float_float = 0
        else:
            short_float_float = float(short_float[:-1])/100

        # gets revenue growth
        stock_dic[ticker] = {'company_name': company_name, 'ticker': ticker, 'industry': industry, 'beta': beta, 'mkt_cap' : mkt_cap,'mkt_cap_short': mkt_cap_short, 'revenue': revenue, 'revenue_short':revenue_short,'profit': profit, 'profit_short':profit_short, 'profit_margin':profit_margin, 'sector': sector,'rev_growth': rev_growth, 'pe': pe,'fwdpe':fwdpe, 'profit_margin_float': profit_margin_float,'rev_growth_float':rev_growth_float,'ps':ps,'eps':eps,'pb':pb,'avg_volume':avg_volume,'shares_float':shares_float,'short_float':short_float,'book_value':book_value,'bvps':bvps,'avg_volume_float':avg_volume_float,'shares_float_float':shares_float_float,'short_float_float':short_float_float}
    return stock_dic
# Creates a stock dictionary for the industry
def get_industry_info(ind):
    industry = ind
    foverview = Valuation()
    filters_dict = {'Industry': industry}
    foverview.set_filter(filters_dict=filters_dict)
    avg_pe = None
    avg_eps = None
    avg_fwdpe = None
    avg_pb = None
    avg_ps = None
    avg_mkt_cap = None
    while avg_pe == None or avg_eps == None or avg_fwdpe == None or avg_pb == None or avg_ps == None or avg_mkt_cap == None:
        try:
            df = foverview.screener_view()
            time.sleep(5)
            mkt_cap_list1 = df ['Market Cap']
            mkt_cap_list2 = []
            ps_list1 = df['P/S']
            ps_list2 = []
            pb_list1 = df['P/B']
            pb_list2 = []
            pe_list1 = df['P/E']
            pe_list2 = []
            eps_list1 = df['EPS this Y']
            eps_list2 = []
            fwdpe_list1 = df['Fwd P/E']
            fwdpe_list2 = []
            for mkt_cap in mkt_cap_list1:
                if math.isnan(mkt_cap):
                    continue
                else:
                    mkt_cap_list2.append(mkt_cap)
                    continue
            for fwdpe in fwdpe_list1:
                if math.isnan(fwdpe):
                    continue
                else:
                    fwdpe_list2.append(fwdpe)
                    continue
            for eps in eps_list1:
                if math.isnan(eps):
                    continue
                else:
                    eps_list2.append(eps)
                    continue
            for ps in ps_list1:
                if math.isnan(ps):
                    continue
                else:
                    ps_list2.append(ps)
                    continue
            for pe in pe_list1:
                if math.isnan(pe):
                    continue
                else:
                    pe_list2.append(pe)
                    continue
            for pb in pb_list1:
                if math.isnan(pb):
                    continue
                else:
                    pb_list2.append(pb)
                    continue
            avg_ps = round(statistics.mean(ps_list2),2)
            avg_pe = round(statistics.mean(pe_list2),2)
            avg_pb = round(statistics.mean(pb_list2),2)
            avg_eps = round(statistics.mean(eps_list2),2)
            avg_fwdpe = round(statistics.mean(fwdpe_list2),2)
            avg_mkt_cap = round(statistics.mean(mkt_cap_list2),2)
            ind_size = sum(mkt_cap_list2)
            IndustryInfo.objects.filter(name=industry).update(avg_pe=avg_pe,avg_ps=avg_ps,avg_pb=avg_pb,avg_eps=avg_eps,avg_fwdpe=avg_fwdpe,avg_mkt_cap=avg_mkt_cap,ind_size=ind_size)
        except Exception:
            time.sleep(30)
# Gets Industry data


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
    return small_industries
# Gets a list of all the industries

# Can run the following in the Terminal:

#  python manage.py crontab remove
#  python manage.py crontab show
#  python manage.py crontab add
#  python manage.py runserver
#  python manage.py crontab run (hash)

def get_ind_av():
    industries = get_industry_list()
    for industry in industries:
        get_industry_info(industry)
# Gets Industry averages, should take roughly 20-30 minutes

def get_stock_info():
    industries = get_industry_list()
    industries = industries[:2]
    for industry in industries:
        get_stock_dic(industry)
        for stock in stock_dic:
            StockTest.objects.update_or_create(
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
                short_float_float=stock_dic[stock]['short_float_float']

                )
# Gets all data on all stocks and stores it

def get_bigindustry_list():
    req = Request("https://finviz.com/groups.ashx?g=industry&v=110&#o=name",headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read().decode('utf-8')
    industries = re.findall('(?<=class="tab-link">).*?(?=</a>)',webpage,re.DOTALL)
    industries = industries[:144]
    big_industries = [industries[13],industries[17],industries[118],industries[8],industries[9],industries[37],industries[40],industries[43],industries[44],industries[62],industries[120],industries[121]]
    small_industries = []
    for industry in industries:
        if industry not in big_industries:
            small_industries.append(industry)
    return big_industries

big_stock_dic={}

def get_big_stock_dic():
    bigindlist = get_industry_list()
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
            
    big_ticka_list = []

    def add_tickers_to_list(tickalist):
        try:
            for ticker in tickalist:
                if ticker not in big_ticka_list:
                    big_ticka_list.append(ticker)
                else: continue
        except:
            pass

    def get_tickers_from_page(i,page):
        reqdef1 = Request('https://finviz.com/screener.ashx?f=ind_'+i+'&r='+page, headers={'User-Agent': 'Mozilla/5.0'})
        urlsite = urlopen(reqdef1).read().decode('utf-8')
        tickalist = re.findall('(?<=class="screener-link-primary">).*?(?=</a>)',urlsite, re.DOTALL)
        return add_tickers_to_list(tickalist)
    for i in newbigindlist:
        for page in rlist:
            try:
                get_tickers_from_page(i,page)
                time.sleep(.3)
            except Exception:
                time.sleep(3)
    for stock_ticker in big_ticka_list:
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

        industry = stock['Industry']
        
        pb = stock['P/B']
        pb = fix_dashes(pb)
        ps = stock['P/S']
        ps = fix_dashes(ps)
        pe = stock['P/E']
        pe = fix_dashes(pe)
        fwdpe = stock['Forward P/E']
        fwdpe = fix_dashes(fwdpe)
        eps = stock['EPS (ttm)']
        eps = fix_dashes(eps)
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
        
        short_float = stock['Short Float']

        if short_float == '-':
            short_float = str(0)
            short_float_float = 0
        else:
            short_float_float = float(short_float[:-1])/100

        # gets revenue growth
        big_stock_dic[ticker] = {'company_name': company_name, 'ticker': ticker, 'industry': industry, 'beta': beta, 'mkt_cap' : mkt_cap,'mkt_cap_short': mkt_cap_short, 'revenue': revenue, 'revenue_short':revenue_short,'profit': profit, 'profit_short':profit_short, 'profit_margin':profit_margin, 'sector': sector,'rev_growth': rev_growth, 'pe': pe,'fwdpe':fwdpe, 'profit_margin_float': profit_margin_float,'rev_growth_float':rev_growth_float,'ps':ps,'eps':eps,'pb':pb,'avg_volume':avg_volume,'shares_float':shares_float,'short_float':short_float,'book_value':book_value,'bvps':bvps,'avg_volume_float':avg_volume_float,'shares_float_float':shares_float_float,'short_float_float':short_float_float}
    return big_stock_dic

def get_big_stock_info():
    get_big_stock_dic()
    for stock in big_stock_dic:
        StockTest.objects.update_or_create(
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
            short_float_float=stock_dic[stock]['short_float_float']
            )