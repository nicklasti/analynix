from django.contrib import admin
from myapp.models import StockInfo,BestStocks,WorstStocks
admin.site.register(StockInfo)
admin.site.register(BestStocks)
admin.site.register(WorstStocks)