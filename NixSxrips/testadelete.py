from cmath import nan
from finvizfinance.quote import finvizfinance
from finvizfinance.screener.overview import Overview
import math
import statistics
from urllib.request import Request, urlopen
import regex as re
from finvizfinance.quote import finvizfinance
import time

text = 'AAWW'
price_to_earnings = finvizfinance(text).ticker_fundament()['P/E']


industry = finvizfinance(text).ticker_fundament()['Industry'] ###already in my script

foverview = Overview()
filters_dict = {'Industry': industry}
foverview.set_filter(filters_dict=filters_dict)
print(foverview.set_filter(filters_dict=filters_dict))
df = foverview.screener_view()
pe_list1 = (df['P/E'])
pe_list2 = []
for pe in pe_list1:
    if math.isnan(pe):
        continue
    else:
        pe_list2.append(pe)
        continue
avg_pe = round(statistics.mean(pe_list2),2)