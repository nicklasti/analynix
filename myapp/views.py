from audioop import avg
from unicodedata import name
from django.shortcuts import render
from django.http import HttpResponse
import yfinance as yf
from urllib.request import Request, urlopen
import re
import yahoo_fin
from yahoo_fin import options
from yahoo_fin import stock_info
import pandas_datareader as pdr
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta
import datetime
from datetime import datetime
from datetime import date
from datetime import time
from finvizfinance.quote import finvizfinance
from finvizfinance.screener.overview import Overview
import math
import statistics
import time
import plotly.graph_objects as go
from plotly.offline import plot
import pandas as pd
import requests
from myapp.models import IndustryInfo
# Imports necessary packages
today = date.today()
date_1y = datetime.now() - relativedelta(years=1)
date_2y = datetime.now() - relativedelta(years=2)
date_3y = datetime.now() - relativedelta(years=3)
date_5y = datetime.now() - relativedelta(years=5)
date_10y = datetime.now() - relativedelta(years=10)
date_250y = datetime.now() - relativedelta(years=250)
date_ytd = datetime(today.year, 1,1)
# Creates date choices for the chart
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
def index(request):
    return render(request, 'index.html')
    # Renders the index
def overview(request):
    text = request.GET['text']
    # Pulls the ticker from the index.html form
    stock = finvizfinance(text).ticker_fundament()
    # Stores the basic stock data as a variable
    industry = stock['Industry']
    # Gets the industry
    sector = stock['Sector']
    # Gets the sector
    ticker = text.upper()
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
    #
    mkt_cap_short = stock['Market Cap']
    mkt_cap = float(mkt_cap_short[:-1]) * float(DOLLAR_MAPPING[mkt_cap_short[-1]])
    #gets mkt cap
    revenue_short = stock['Sales']
    revenue = float(revenue_short[:-1]) * float(DOLLAR_MAPPING[revenue_short[-1]])
    # gets the sales
    profit = stock['Income']
    # gets the net income
    profit_margin = stock['Profit Margin']
    # gets the PM
    rev_growth = stock['Sales Q/Q']
    avg_volume = stock['Avg Volume']
    shares_float = stock['Shs Float']
    short_float = stock['Short Float']
    # gets revenue growth

    df1 = pdr.data.get_data_yahoo(ticker, start='1970-1-1', end=today)
    pryce = df1['Close']
    pryce = pryce.values.tolist()
    df1 = pdr.data.get_data_yahoo(ticker, start='1970-1-1', end=today)
    deight1 = df1['Close']
    deight = deight1.index.tolist()
    deight = [datetime.strftime(d, '%Y-%m-%d') for d in deight]
    date_max = deight[0]
    df1 = pdr.data.get_data_yahoo(ticker, start=date_max, end=today)
    pryce = df1['Close']
    pryce = pryce.values.tolist()
    df1 = pdr.data.get_data_yahoo(ticker, start=date_max, end=today)
    deight1 = df1['Close']
    deight = deight1.index.tolist()
    deight = [datetime.strftime(d, '%Y-%m-%d') for d in deight]
    # Gets Prices and Corresponding Dates

    def line():
        figure = go.Figure(data=[go.Line(x=deight,y=pryce)])
        figure.update_xaxes(rangeslider_visible=True, 
                            rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")]) , font_color="black"))
        figure.update_layout(plot_bgcolor='#dddddd', paper_bgcolor ='#dddddd', font_color="black", title_font_color="black")
        figure.update_traces(line_color="black")
        figure.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='#a5a5a5')
        figure.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='#a5a5a5')
        line_div = plot(figure, output_type='div')
        return line_div
    # Creates chart

    avg_list = IndustryInfo.objects.values()
    for x in avg_list:
        if x['name'] == industry:
            avg_pe = x['avg_pe']
            avg_ps = x['avg_ps']
            avg_pb = x['avg_pb']
            avg_eps = x['avg_eps']
            avg_fwdpe = x['avg_fwdpe']
    # Gets variables from IndustryInfo object

    return render(request, 'overview.html', {'company_name': company_name, 'ticker': ticker, 'industry': industry, 'beta': beta, 'mkt_cap' : mkt_cap,'mkt_cap_short': mkt_cap_short, 'revenue': revenue, 'revenue_short':revenue_short,'profit': profit, 'profit_margin':profit_margin, 'sector': sector,'rev_growth': rev_growth, 'deight': deight, 'pryce': pryce, 'line': line(), 'pe': pe,'fwdpe':fwdpe, 'avg_pe': avg_pe,'avg_ps':avg_ps,'avg_pb':avg_pb,'avg_eps':avg_eps,'avg_fwdpe':avg_fwdpe,'ps':ps,'eps':eps,'pb':pb,'avg_volume':avg_volume,'shares_float':shares_float,'short_float':short_float})
