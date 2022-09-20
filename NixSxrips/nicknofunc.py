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




pe_dic_final = {}

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
for industry in test_list:
    foverview = Overview()
    filters_dict = {'Industry': industry}
    foverview.set_filter(filters_dict=filters_dict)
    df = pd.DataFrame()
    df = foverview.screener_view()
    print(df)
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
            pe_dic_final[industry] = avg_pe
        except Exception:
            time.sleep(0.5)

print(pe_dic_final)

