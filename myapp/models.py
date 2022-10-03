# Creates objects in the Sqlite3 Daztabase
from pickle import TRUE
from django.db import models

class StockInfo(models.Model):
    name = models.TextField(default='default',primary_key=TRUE)
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
    avg_volume_float = models.FloatField(default=69.69)
    avg_volume = models.TextField(default='default')
    shares_float = models.TextField(default='default')
    short_float = models.TextField(default='default')
    book_value = models.FloatField(default=0)
    bvps = models.FloatField(default=0)
    avg_volume_float = models.FloatField(default=0)
    shares_float_float = models.FloatField(default=0)
    short_float_float = models.FloatField(default=0)
    prices = models.JSONField(default=dict)
    dates = models.JSONField(default=dict)
    def __str__(self):
        return self.name

class Cronjobtest(models.Model):
    tester = models.TextField(default='default')