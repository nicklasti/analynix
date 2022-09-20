from audioop import avg
import math
from pickle import TRUE
from urllib.request import Request, urlopen
import regex as re
import statistics
from finvizfinance.screener.overview import Overview
import time
from cmath import nan
import math
import pandas as pd

###

pe_dic = {}

###

def get_avg_pe_step2(industry):
    foverview = Overview()
    filters_dict = {'Industry': industry}
    foverview.set_filter(filters_dict=filters_dict)
    avg_pe = None
    while avg_pe == None:
        try:
            df = foverview.screener_view()
            pe_list1 = df['P/E']
            pe_list2 = []
            for pe in pe_list1:
                if math.isnan(pe):
                    continue
                else:
                    pe_list2.append(pe)
                    continue
            avg_pe = round(statistics.mean(pe_list2),2)
            print('done with:',industry)
            time.sleep(10)
        except Exception:
            time.sleep(120)
    return avg_pe


req = Request("https://finviz.com/groups.ashx?g=industry&v=110&#o=name",headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read().decode('utf-8')
industries = re.findall('(?<=class="tab-link">).*?(?=</a>)',webpage,re.DOTALL)
industries = industries[:144]
big_industries = [industries[13],industries[17],industries[118]]
small_industries = []
pe_list = []
for industry in industries:
    if industries in big_industries:
        pass
    else:
        small_industries.append(industry)


test_list = ['Aluminum','Airlines']


###

pe_dic_final = {}

for industry in small_industries:
    pe_dic_final[industry] = get_avg_pe_step2(industry)

print(pe_dic_final)

