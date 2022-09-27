
# Creates objects in the Sqlite3 Daztabase

from pickle import TRUE
from unicodedata import name
from django.db import models
from logging.config import IDENTIFIER

class IndustryInfo(models.Model):
    name = models.TextField(default='default')
    avg_pe = models.FloatField(default=69.69)
    avg_ps = models.FloatField(default=69.69)
    avg_eps = models.FloatField(default=69.69)
    avg_fwdpe  = models.FloatField(default=69.69)
    avg_pb = models.FloatField(default=69.69)
    ind_size = models.FloatField(default=69.69)
    avg_mkt_cap = models.FloatField(default=69.69)

class StockInfo(models.Model):
    name = models.TextField(default='default')
    industry = models.TextField(default='default')
    sector = models.TextField(default='default')
    company_name = models.TextField(default='default')
    beta  = models.FloatField(default=69.69)
    pb = models.FloatField(default=69.69)
    ps = models.FloatField(default=69.69)
    pe = models.FloatField(default=69.69)
    fwdpe = models.FloatField(default=69.69)
    eps = models.FloatField(default=69.69)
    mkt_cap_short = models.TextField(default='default')
    mkt_cap = models.FloatField(default=69.69)
    revenue_short = models.TextField(default='default')
    revenue = models.FloatField(default=69.69)
    profit_short = models.TextField(default='default')
    profit = models.FloatField(default=69.69)
    profit_margin = models.TextField(default='default')
    profit_margin_float = models.FloatField(default=69.69)
    rev_growth = models.TextField(default='default')
    rev_growth_float = models.FloatField(default=69.69)
    avg_volume = models.FloatField(default=69.69)
    shares_float = models.FloatField(default=69.69)
    short_float = models.TextField(default='default')

class StockTest(models.Model):
    name = models.TextField(default='Ticker')
    industry = models.TextField(default='Industry')
    sector = models.TextField(default='Sector')
    company_name = models.TextField(default='Company Name')
    beta = models.FloatField(default=0)
    pb =  models.FloatField(default=0)
    ps =  models.FloatField(default=0)
    pe = models.FloatField(default=0)
    fwdpe = models.FloatField(default=0)
    eps =  models.FloatField(default=0)
    mkt_cap_short = models.TextField(default='Market Cap Short')
    mkt_cap = models.FloatField(default=0)
    revenue_short = models.TextField(default='Revenue Short')
    revenue = models.FloatField(default=0)
    profit_short = models.TextField(default='Profit Short')
    profit = models.FloatField(default=0)
    profit_margin = models.TextField(default='Profit Margin')
    profit_margin_float = models.FloatField(default=0)
    rev_growth = models.TextField(default='Rev Growth')
    rev_growth_float = models.FloatField(default=0)
    avg_volume = models.TextField(default='Avg Volume')
    shares_float = models.TextField(default='Shares Float')
    short_float = models.TextField(default='Short Float')
    book_value = models.FloatField(default=0)
    bvps = models.FloatField(default=0)
    avg_volume_float = models.FloatField(default=0)
    shares_float_float = models.FloatField(default=0)
    short_float_float = models.FloatField(default=0)
    def __str__(self):
        return self.name