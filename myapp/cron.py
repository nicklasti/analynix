
# Periodic Caching System:

from django.db import models
from unicodedata import name
from myapp.models import IndustryInfo
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
from myapp.models import IndustryInfo
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
def fix_dashes(x):
        if x == '-':
            x = ''
            return x
        else:
            x = round(float(x),2)
            return x
    # Gets rid of the dash for - values
def get_stock_info(industry):
    foverview = Valuation()
    filters_dict = {'Industry': industry}
    foverview.set_filter(filters_dict=filters_dict)
    stock == None
    ticker == None
    sector == None
    company_name == None
    beta  == None
    pb == None
    ps == None
    pe == None
    fwdpe == None
    eps == None
    mkt_cap_short == None
    mkt_cap == None
    revenue_short == None
    revenue == None
    profit_short == None
    profit == None
    profit_margin == None
    profit_margin_float == None
    rev_growth == None
    rev_growth_float == None
    avg_volume == None
    shares_float == None
    short_float == None
    df = foverview.screener_view()
    time.sleep(5)
    ticker_list = df['Ticker']
    for stock_ticker in ticker_list:
        while stock == None or sector == None or company_name == None or beta == None or pb == None or ps == None or pe == None or fwdpe == None or eps == None or mkt_cap_short == None or mkt_cap == None or revenue_short == None or revenue == None or profit_short == None or profit == None or profit_margin == None or profit_margin_float == None or rev_growth == None or rev_growth_float == None or avg_volume == None or shares_float == None or short_float == None:
            try:
                stock = finvizfinance(stock_ticker).ticker_fundament()
                time.sleep(5)
                # Stores the basic stock data as a variable
                sector = stock['Sector']
                # Gets the sector
                ticker = stock['Ticker']
                # Gets the ticker
                company_name = stock['Company']
                # Gets the company name
                beta = stock['Beta']
                beta = fix_dashes(beta)
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
                mkt_cap = float(mkt_cap_short[:-1]) * float(DOLLAR_MAPPING[mkt_cap_short[-1]])
                #gets mkt cap
                revenue_short = stock['Sales']
                revenue = float(revenue_short[:-1]) * float(DOLLAR_MAPPING[revenue_short[-1]])
                # gets the sales
                profit_short = stock['Income']
                profit = float(profit_short[:-1]) * float(DOLLAR_MAPPING[profit_short[-1]])
                # gets the net income
                profit_margin = stock['Profit Margin']
                # gets the PM
                profit_margin_float = float(profit_margin[:-1])/100
                rev_growth = stock['Sales Q/Q']
                rev_growth_float = float(rev_growth[:-1])/100
                avg_volume = stock['Avg Volume']
                shares_float = stock['Shs Float']
                short_float = stock['Short Float']
                # gets revenue growth
                StockInfo.objects.update_or_create(ticker=stock_ticker,industry=industry, sector=sector, company_name=company_name,beta=beta,pb=pb,ps=ps,pe=pe,fwdpe=fwdpe,eps=eps,mkt_cap_short=mkt_cap_short,mkt_cap=mkt_cap,revenue_short=revenue_short,revenue=revenue, profit_short=profit_short,profit=profit,profit_margin=profit_margin, profit_margin_float=profit_margin_float, rev_growth=rev_growth, rev_growth_float=rev_growth_float,avg_volume=avg_volume,shares_float=shares_float,short_float=short_float)
            except Exception:
                time.sleep(15)

def get_industry_info(industry):
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

# Can run the following in the Terminal:

#  python manage.py crontab remove
#  python manage.py crontab show
#  python manage.py crontab add
#  python manage.py runserver

def cronjob_every_midnight():
    industries = get_industry_list()
    for industry in industries:
        get_industry_info(industry)
    # Gets Industry averages, should take roughly 20-30 minutes

def cronjob_every_1am():
    industries = get_industry_list()
    for industry in industries:
        get_stock_info(industry)
    # Gets Stock prices, should take long, maybe 4-6 hours