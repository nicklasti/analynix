from django.shortcuts import render
import math
import plotly.graph_objects as go
from plotly.offline import plot
from myapp.models import StockInfo
from django.db import connection 

# Imports necessary packages
# Creates date choices for the chart
DOLLAR_MAPPING = {
    'T': float(1000000000000),
    'B': float(1000000000),
    'M': float(1000000),
    'K': float(1000),
    'e': float(0)
}

def human_format(num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
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

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def copyright(request):
    return render(request, 'copyright.html')



def overview(request):
    text = (request.GET['text']).upper()
    # Pulls the ticker from the index.html form
    avg_list = StockInfo.objects.values()
    for x in avg_list:
        if x['name'] == text:
            ticker = x['name']
            industry = x['industry']
            sector = x['sector']
            company_name = x['company_name']
            beta = x['beta']
            pb = x['pb']
            pb_float = pb
            if pb == 0:
                pb = 'N/A'
            ps = x['ps']
            ps_float = ps
            if ps == 0:
                ps = 'N/A'
            pe = x['pe']
            pe_float=pe
            if pe == 0:
                pe = 'N/A'
            fwdpe = x['fwdpe']
            fwdpe_float = fwdpe
            if fwdpe == 0:
                fwdpe = 'N/A'
            eps = x['eps']
            eps_float = eps
            if fwdpe == 0:
                fwdpe = 'N/A'
            mkt_cap_short = x['mkt_cap_short']
            mkt_cap = x['mkt_cap']
            revenue_short = x['revenue_short']
            revenue = x['revenue']
            profit_short = x['profit_short']
            profit = x['profit']
            profit_margin = x['profit_margin']
            profit_margin_float = x['profit_margin_float']
            if profit == 0:
                profit_margin='N/A'
            rev_growth = x['rev_growth']
            if revenue == 0:
                rev_growth == 'N/A'
            rev_growth_float = x['rev_growth_float']
            avg_volume = x['avg_volume']
            shares_float = x['shares_float']
            short_float = x['short_float']
            if short_float == '-':
                short_float = str(0)
            book_value = x['book_value']
            if book_value == '-':
                book_value = 0
            bvps = x['bvps']
            avg_volume_float = x['avg_volume_float']
            shares_float_float =x['shares_float_float']
            short_float_float =x['short_float_float']
            prices = x['prices']
            prices = prices['prices']
            dates = x['dates']
            dates = dates['dates']

    def line():
        figure = go.Figure(data=[go.Line(x=dates,y=prices)])
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

    cursor = connection.cursor()
    cursor.execute('SELECT name, AVG(pe) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    avg_pe = cursor.fetchall()
    for x in avg_pe:
        avg_pe = float(x[1])

    cursor = connection.cursor()
    cursor.execute('SELECT name, AVG(ps) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    avg_ps = cursor.fetchall()
    for x in avg_ps:
        avg_ps = float(x[1])

    cursor = connection.cursor()
    cursor.execute('SELECT name, AVG(pb) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    avg_pb = cursor.fetchall()
    for x in avg_pb:
        avg_pb = float(x[1])

    cursor = connection.cursor()
    cursor.execute('SELECT name, AVG(eps) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    avg_eps = cursor.fetchall()
    for x in avg_eps:
        avg_eps = float(x[1])

    cursor = connection.cursor()
    cursor.execute('SELECT name, AVG(fwdpe) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    avg_fwdpe = cursor.fetchall()
    for x in avg_fwdpe:
        avg_fwdpe = float(x[1])

    cursor = connection.cursor()
    cursor.execute('SELECT name, AVG(mkt_cap) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    avg_mkt_cap = cursor.fetchall()
    for x in avg_mkt_cap:
        avg_mkt_cap = x[1]

    cursor = connection.cursor()
    cursor.execute('SELECT name, COUNT(revenue) FROM myapp_stockinfo WHERE industry = %s',[industry])
    numba_o_stocks_in_industry = cursor.fetchall()
    for x in numba_o_stocks_in_industry:
        numba_o_stocks_in_industry = float(x[1])

    cursor = connection.cursor()
    cursor.execute('SELECT name, SUM(mkt_cap) FROM myapp_stockinfo WHERE industry = %s',[industry])
    ind_size = cursor.fetchall()
    for x in ind_size:
        ind_size = float(x[1])    

    try:
        dtc = round(((short_float_float * shares_float_float)/avg_volume_float),2)
    except Exception:
        dtc = 0

    revenue_short = human_format(revenue)
    profit_short = human_format(profit)

    mkt_share = '{:.2%}'.format(mkt_cap/ind_size)

    ind_size = human_format(ind_size)

    avg_mkt_cap = human_format(avg_mkt_cap)
    
    cursor = connection.cursor()
    cursor.execute('SELECT name, AVG(revenue) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    avg_rev = cursor.fetchall()
    for x in avg_rev:
        avg_rev = human_format(x[1])
        avg_rev_float = x[1]
    
    how_much_above_or_below = revenue - avg_rev_float

    cursor = connection.cursor()
    cursor.execute('SELECT AVG(revenue*revenue) - AVG(revenue)*AVG(revenue) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    top_var = cursor.fetchall()
    for x in top_var:
        top_var = x[0]
    var = top_var/numba_o_stocks_in_industry
    stdev = math.sqrt(var)
    how_many_stdevs= how_much_above_or_below/stdev
    if how_many_stdevs >= 5:
        grade = 'A+'
    elif how_many_stdevs >= 4:
        grade = 'A'
    elif how_many_stdevs >= 3.8:
        grade = 'A-'
    elif how_many_stdevs >= 3:
        grade = 'B+'
    elif how_many_stdevs >= 1:
        grade = 'B'
    elif how_many_stdevs >= 0:
        grade = 'B-'
    elif how_many_stdevs >= -1:
        grade = 'C+'
    elif how_many_stdevs >= -2:
        grade = 'C'
    elif how_many_stdevs >= -3.:
        grade = 'C-'
    elif how_many_stdevs >= -3.4:
        grade = 'D+'
    elif how_many_stdevs >= -3.7:
        grade = 'D'
    elif how_many_stdevs >= -3.8:
        grade = 'D-'
    elif how_many_stdevs >= -3.9:
        grade = 'F'
    elif how_many_stdevs < -3.9:
        grade = 'F-'
    

    cursor = connection.cursor()
    cursor.execute('SELECT name, AVG(profit) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    avg_profit = cursor.fetchall()
    for x in avg_profit:
        avg_profit = human_format(x[1])
        avg_profit_float = x[1]

    profit_dif = profit - avg_profit_float

    cursor = connection.cursor()
    cursor.execute('SELECT AVG(profit*profit) - AVG(profit)*AVG(profit) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    profit_top_var = cursor.fetchall()
    for x in profit_top_var:
        profit_top_var = x[0]
    profit_var = profit_top_var/numba_o_stocks_in_industry
    profit_stdev = math.sqrt(profit_var)
    profit_stdevs = profit_dif/profit_stdev
    if profit_stdevs >= 5:
        profit_grade = 'A+'
    elif profit_stdevs >= 4:
        profit_grade = 'A'
    elif profit_stdevs >= 3.8:
        profit_grade = 'A-'
    elif profit_stdevs >= 3:
        profit_grade = 'B+'
    elif profit_stdevs >= 1:
        profit_grade = 'B'
    elif profit_stdevs >= 0:
        profit_grade = 'B-'
    elif profit_stdevs >= -1:
        profit_grade = 'C+'
    elif profit_stdevs >= -2:
        profit_grade = 'C'
    elif profit_stdevs >= -3.:
        profit_grade = 'C-'
    elif profit_stdevs >= -3.4:
        profit_grade = 'D+'
    elif profit_stdevs >= -3.7:
        profit_grade = 'D'
    elif profit_stdevs >= -3.8:
        profit_grade = 'D-'
    elif profit_stdevs >= -3.9:
        profit_grade = 'F'
    elif profit_stdevs < -3.9:
        profit_grade = 'F-'
        
    cursor = connection.cursor()
    cursor.execute('SELECT name, AVG(rev_growth_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    avg_rev_growth = cursor.fetchall()
    for x in avg_rev_growth:
        avg_rev_growth = '{:.2%}'.format(x[1])
        avg_rev_growth_float = x[1]

    rev_growth_dif = rev_growth_float - avg_rev_growth_float

    cursor = connection.cursor()
    cursor.execute('SELECT AVG(rev_growth_float*rev_growth_float) - AVG(rev_growth_float)*AVG(rev_growth_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    rev_growth_top_var = cursor.fetchall()
    for x in rev_growth_top_var:
        rev_growth_top_var = x[0]
    rev_growth_var = rev_growth_top_var/numba_o_stocks_in_industry
    rev_growth_stdev = math.sqrt(rev_growth_var)
    rev_growth_stdevs = rev_growth_dif/rev_growth_stdev
    if revenue == 'N/A':
        rev_growth_grade = 'N/A'
    elif rev_growth_stdevs >= 5:
        rev_growth_grade = 'A+'
    elif rev_growth_stdevs >= 4:
        rev_growth_grade = 'A'
    elif rev_growth_stdevs >= 3.8:
        rev_growth_grade = 'A-'
    elif rev_growth_stdevs >= 3:
        rev_growth_grade = 'B+'
    elif rev_growth_stdevs >= 1:
        rev_growth_grade = 'B'
    elif rev_growth_stdevs >= 0:
        rev_growth_grade = 'B-'
    elif rev_growth_stdevs >= -1:
        rev_growth_grade = 'C+'
    elif rev_growth_stdevs >= -2:
        rev_growth_grade = 'C'
    elif rev_growth_stdevs >= -3.:
        rev_growth_grade = 'C-'
    elif rev_growth_stdevs >= -3.4:
        rev_growth_grade = 'D+'
    elif rev_growth_stdevs >= -3.7:
        rev_growth_grade = 'D'
    elif rev_growth_stdevs >= -3.8:
        rev_growth_grade = 'D-'
    elif rev_growth_stdevs >= -3.9:
        rev_growth_grade = 'F'
    elif rev_growth_stdevs < -3.9:
        rev_growth_grade = 'F-'

    cursor = connection.cursor()
    cursor.execute('SELECT name, AVG(profit_margin_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    avg_profit_margin = cursor.fetchall()
    for x in avg_profit_margin:
        avg_profit_margin = '{:.2%}'.format(x[1])
        avg_profit_margin_float = x[1]

    profit_margin_dif = profit_margin_float - avg_profit_margin_float

    cursor = connection.cursor()
    cursor.execute('SELECT AVG(profit_margin_float*profit_margin_float) - AVG(profit_margin_float)*AVG(profit_margin_float) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    profit_margin_top_var = cursor.fetchall()
    for x in profit_margin_top_var:
        profit_margin_top_var = x[0]
    profit_margin_var = profit_margin_top_var/numba_o_stocks_in_industry
    profit_margin_stdev = math.sqrt(profit_margin_var)
    profit_margin_stdevs = profit_margin_dif/profit_margin_stdev
    if profit_margin == "N/A":
        profit_margin_grade = 'N/A'
    elif profit_margin_stdevs >= 5:
        profit_margin_grade = 'A+'
    elif profit_margin_stdevs >= 4:
        profit_margin_grade = 'A'
    elif profit_margin_stdevs >= 3.8:
        profit_margin_grade = 'A-'
    elif profit_margin_stdevs >= 3:
        profit_margin_grade = 'B+'
    elif profit_margin_stdevs >= 1:
        profit_margin_grade = 'B'
    elif profit_margin_stdevs >= 0:
        profit_margin_grade = 'B-'
    elif profit_margin_stdevs >= -1:
        profit_margin_grade = 'C+'
    elif profit_margin_stdevs >= -2:
        profit_margin_grade = 'C'
    elif profit_margin_stdevs >= -3.:
        profit_margin_grade = 'C-'
    elif profit_margin_stdevs >= -3.4:
        profit_margin_grade = 'D+'
    elif profit_margin_stdevs >= -3.7:
        profit_margin_grade = 'D'
    elif profit_margin_stdevs >= -3.8:
        profit_margin_grade = 'D-'
    elif profit_margin_stdevs >= -3.9:
        profit_margin_grade = 'F'
    elif profit_margin_stdevs < -3.9:
        profit_margin_grade = 'F-'

    pe_dif = avg_pe - pe_float

    cursor = connection.cursor()
    cursor.execute('SELECT AVG(pe*pe) - AVG(pe)*AVG(pe) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    pe_top_var = cursor.fetchall()
    for x in pe_top_var:
        pe_top_var = x[0]
    pe_var = pe_top_var/numba_o_stocks_in_industry
    pe_stdev = math.sqrt(pe_var)
    pe_stdevs = pe_dif/pe_stdev
    if pe == 'N/A':
        pe_grade = 'N/A'
    elif pe_stdevs >= 5:
        pe_grade = 'A+'
    elif pe_stdevs >= 4:
        pe_grade = 'A'
    elif pe_stdevs >= 3.8:
        pe_grade = 'A-'
    elif pe_stdevs >= 3:
        pe_grade = 'B+'
    elif pe_stdevs >= 1:
        pe_grade = 'B'
    elif pe_stdevs >= 0:
        pe_grade = 'B-'
    elif pe_stdevs >= -1:
        pe_grade = 'C+'
    elif pe_stdevs >= -2:
        pe_grade = 'C'
    elif pe_stdevs >= -3.:
        pe_grade = 'C-'
    elif pe_stdevs >= -3.4:
        pe_grade = 'D+'
    elif pe_stdevs >= -3.7:
        pe_grade = 'D'
    elif pe_stdevs >= -3.8:
        pe_grade = 'D-'
    elif pe_stdevs >= -3.9:
        pe_grade = 'F'
    elif pe_stdevs < -3.9:
        pe_grade = 'F-'

    ps_dif = avg_ps - ps_float
    
    cursor = connection.cursor()
    cursor.execute('SELECT AVG(ps*ps) - AVG(ps)*AVG(ps) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    ps_top_var = cursor.fetchall()
    for x in ps_top_var:
        ps_top_var = x[0]
    ps_var = ps_top_var/numba_o_stocks_in_industry
    ps_stdev = math.sqrt(ps_var)
    ps_stdevs = ps_dif/ps_stdev
    if ps == 'N/A':
        pb_grade = 'N/A'
    elif ps_stdevs >= 5:
        ps_grade = 'A+'
    elif ps_stdevs >= 4:
        ps_grade = 'A'
    elif ps_stdevs >= 3.8:
        ps_grade = 'A-'
    elif ps_stdevs >= 3:
        ps_grade = 'B+'
    elif ps_stdevs >= 1:
        ps_grade = 'B'
    elif ps_stdevs >= 0:
        ps_grade = 'B-'
    elif ps_stdevs >= -1:
        ps_grade = 'C+'
    elif ps_stdevs >= -2:
        ps_grade = 'C'
    elif ps_stdevs >= -3.:
        ps_grade = 'C-'
    elif ps_stdevs >= -3.4:
        ps_grade = 'D+'
    elif ps_stdevs >= -3.7:
        ps_grade = 'D'
    elif ps_stdevs >= -3.8:
        ps_grade = 'D-'
    elif ps_stdevs >= -3.9:
        ps_grade = 'F'
    elif ps_stdevs < -3.9:
        ps_grade = 'F-'

    eps_dif = avg_eps - eps_float
    
    cursor = connection.cursor()
    cursor.execute('SELECT AVG(eps*eps) - AVG(eps)*AVG(eps) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    eps_top_var = cursor.fetchall()
    for x in eps_top_var:
        eps_top_var = x[0]
    eps_var = eps_top_var/numba_o_stocks_in_industry
    eps_stdev = math.sqrt(eps_var)
    eps_stdevs = eps_dif/eps_stdev
    if eps == 'N/A':
        eps_grade = 'N/A'
    elif eps_stdevs >= 5:
        eps_grade = 'A+'
    elif eps_stdevs >= 4:
        eps_grade = 'A'
    elif eps_stdevs >= 3.8:
        eps_grade = 'A-'
    elif eps_stdevs >= 3:
        eps_grade = 'B+'
    elif eps_stdevs >= 1:
        eps_grade = 'B'
    elif eps_stdevs >= 0:
        eps_grade = 'B-'
    elif eps_stdevs >= -1:
        eps_grade = 'C+'
    elif eps_stdevs >= -2:
        eps_grade = 'C'
    elif eps_stdevs >= -3.:
        eps_grade = 'C-'
    elif eps_stdevs >= -3.4:
        eps_grade = 'D+'
    elif eps_stdevs >= -3.7:
        eps_grade = 'D'
    elif eps_stdevs >= -3.8:
        eps_grade = 'D-'
    elif eps_stdevs >= -3.9:
        eps_grade = 'F'
    elif eps_stdevs < -3.9:
        eps_grade = 'F-'
    
    fwdpe_dif = avg_fwdpe - fwdpe_float
    
    cursor = connection.cursor()
    cursor.execute('SELECT AVG(fwdpe*fwdpe) - AVG(fwdpe)*AVG(fwdpe) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    fwdpe_top_var = cursor.fetchall()
    for x in fwdpe_top_var:
        fwdpe_top_var = x[0]
    fwdpe_var = fwdpe_top_var/numba_o_stocks_in_industry
    fwdpe_stdev = math.sqrt(fwdpe_var)
    fwdpe_stdevs = fwdpe_dif/fwdpe_stdev
    if fwdpe == 'N/A':
        fwdpe_grade = 'N/A'
    elif fwdpe_stdevs >= 5:
        fwdpe_grade = 'A+'
    elif fwdpe_stdevs >= 4:
        fwdpe_grade = 'A'
    elif fwdpe_stdevs >= 3.8:
        fwdpe_grade = 'A-'
    elif fwdpe_stdevs >= 3:
        fwdpe_grade = 'B+'
    elif fwdpe_stdevs >= 1:
        fwdpe_grade = 'B'
    elif fwdpe_stdevs >= 0:
        fwdpe_grade = 'B-'
    elif fwdpe_stdevs >= -1:
        fwdpe_grade = 'C+'
    elif fwdpe_stdevs >= -2:
        fwdpe_grade = 'C'
    elif fwdpe_stdevs >= -3.:
        fwdpe_grade = 'C-'
    elif fwdpe_stdevs >= -3.4:
        fwdpe_grade = 'D+'
    elif fwdpe_stdevs >= -3.7:
        fwdpe_grade = 'D'
    elif fwdpe_stdevs >= -3.8:
        fwdpe_grade = 'D-'
    elif fwdpe_stdevs >= -3.9:
        fwdpe_grade = 'F'
    elif fwdpe_stdevs < -3.9:
        fwdpe_grade = 'F-'

    pb_dif = avg_pb - pb_float
    
    cursor = connection.cursor()
    cursor.execute('SELECT AVG(pb*pb) - AVG(pb)*AVG(pb) FROM myapp_stockinfo WHERE industry = %s GROUP BY industry',[industry])
    pb_top_var = cursor.fetchall()
    for x in pb_top_var:
        pb_top_var = x[0]
    pb_var = pb_top_var/numba_o_stocks_in_industry
    pb_stdev = math.sqrt(pb_var)
    pb_stdevs = pb_dif/pb_stdev
    if pb == 'N/A':
        pb_grade = 'N/A'
    elif pb_stdevs >= 5:
        pb_grade = 'A+'
    elif pb_stdevs >= 4:
        pb_grade = 'A'
    elif pb_stdevs >= 3.8:
        pb_grade = 'A-'
    elif pb_stdevs >= 3:
        pb_grade = 'B+'
    elif pb_stdevs >= 1:
        pb_grade = 'B'
    elif pb_stdevs >= 0:
        pb_grade = 'B-'
    elif pb_stdevs >= -1:
        pb_grade = 'C+'
    elif pb_stdevs >= -2:
        pb_grade = 'C'
    elif pb_stdevs >= -3.:
        pb_grade = 'C-'
    elif pb_stdevs >= -3.4:
        pb_grade = 'D+'
    elif pb_stdevs >= -3.7:
        pb_grade = 'D'
    elif pb_stdevs >= -3.8:
        pb_grade = 'D-'
    elif pb_stdevs >= -3.9:
        pb_grade = 'F'
    elif pb_stdevs < -3.9:
        pb_grade = 'F-'

    if book_value == '-':
        book_value = 0
    else:
        book_value = human_format(book_value)

    avg_pe = round(avg_pe,2)
    avg_eps = round(avg_eps,2)
    avg_ps = round(avg_ps,2)
    avg_pb = round(avg_pb,2)
    avg_fwdpe = round(avg_fwdpe,2)

    edgar_link_8k = 'https://www.sec.gov/edgar/search/#/q='+text+'&filter_forms=8-K'
    edgar_link_10k = 'https://www.sec.gov/edgar/search/#/q='+text+'&filter_forms=10-K'
    edgar_link_10q = 'https://www.sec.gov/edgar/search/#/q='+text+'&filter_forms=10-Q'
        

    return render(request, 'overview.html', {'company_name': company_name, 'ticker': ticker, 'industry': industry, 'beta': beta, 'mkt_cap' : mkt_cap,'mkt_cap_short': mkt_cap_short, 'revenue': revenue, 'revenue_short':revenue_short,'profit': profit, 'profit_short': profit_short, 'profit_margin':profit_margin, 'profit_margin_float':profit_margin_float, 'sector': sector,'rev_growth': rev_growth, 'rev_growth_float':rev_growth_float,'dates': dates, 'prices': prices, 'line': line(), 'pe': pe,'fwdpe':fwdpe, 'avg_pe': avg_pe,'avg_ps':avg_ps,'avg_pb':avg_pb,'avg_eps':avg_eps,'avg_fwdpe':avg_fwdpe,'ps':ps,'eps':eps,'pb':pb,'avg_volume':avg_volume,'shares_float':shares_float,'short_float':short_float,'avg_mkt_cap':avg_mkt_cap,'ind_size':ind_size,'mkt_share':mkt_share,'avg_rev':avg_rev,'avg_profit':avg_profit,'avg_rev_growth':avg_rev_growth,'avg_profit_margin':avg_profit_margin, 'grade':grade,'how_many_stdevs':how_many_stdevs,'profit_grade':profit_grade,'rev_growth_grade':rev_growth_grade,'profit_margin_grade':profit_margin_grade,'pe_grade':pe_grade,'ps_grade':ps_grade,'pb_grade':pb_grade,'eps_grade':eps_grade,'fwdpe_grade':fwdpe_grade,'edgar_link_10q':edgar_link_10q,'edgar_link_8k':edgar_link_8k, 'edgar_link_10k':edgar_link_10k,'dtc':dtc,'book_value':book_value})
