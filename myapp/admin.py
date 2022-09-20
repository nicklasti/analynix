from django.contrib import admin

# Register your models here.
from myapp.models import IndustryInfo
admin.site.register(IndustryInfo)

from myapp.models import StockInfo
admin.site.register(StockInfo)