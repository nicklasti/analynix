from pickle import TRUE
from unicodedata import name
from django.db import models
from logging.config import IDENTIFIER
# Create your models here.

class IndustryInfo(models.Model):
    name = models.TextField(default='default')
    avg_pe = models.FloatField(default=69.69)
    avg_ps = models.FloatField(default=69.69)
    avg_eps = models.FloatField(default=69.69)
    avg_fwdpe  = models.FloatField(default=69.69)
    avg_pb = models.FloatField(default=69.69)

class StockInfo(models.Model):
    ticker = models.TextField(default='default')
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