from django.shortcuts import render, get_object_or_404,redirect
import math
import plotly.graph_objects as go
from plotly.offline import plot
from myapp.models import StockInfo, BestStocks, WorstStocks
from django.db import connection 

from django.conf import settings
 
 
def error_404_view(request, exception):
   
    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, '404.html')

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
    template = 'overview.html'
    text = (request.GET['text']).upper()
    stock = get_object_or_404(StockInfo, name=text)

    def chart():
        figure = go.Figure(data=[go.Line(x=stock.dates,y=stock.prices)])
        config = {'displayModeBar': False}
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
        figure.update_yaxes(autorange=True, showline=True, linewidth=2, linecolor='black', gridcolor='#a5a5a5')
        figure.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        )
        line_div = plot(figure, output_type='div',config = {'displayModeBar': False})
        #figure.update_layout(displayModeBar=False)
        return line_div
    # Creates chart

    edgar_link_8k = 'https://www.sec.gov/edgar/search/#/q='+text+'&filter_forms=8-K'
    edgar_link_10k = 'https://www.sec.gov/edgar/search/#/q='+text+'&filter_forms=10-K'
    edgar_link_10q = 'https://www.sec.gov/edgar/search/#/q='+text+'&filter_forms=10-Q'

    context = {
        'edgar_link_8k':edgar_link_8k,
        'edgar_link_10k':edgar_link_10k,
        'edgar_link_10q':edgar_link_10q,
        'stock':stock,
        'chart': chart(),

    }

    return render(request,template,context)


def error_404_view(request, exception):
	return render(request, '404.html')

def beststocks(request):
    template = 'beststocks.html'
    stock = BestStocks.objects.values()
    print(stock)
    best_stock_list = []
    for ticker in stock:
        symb = ticker['name']
        obj = get_object_or_404(StockInfo, name=symb)
        best_stock_list.append(obj)

    one = stock[0]['name']
    two = stock [1]['name']
    three = stock[2]['name']
    four = stock[3]['name']
    five = stock[4]['name']
    six = stock[5]['name']
    seven = stock[6]['name']
    eight = stock[7]['name']
    nine = stock[8]['name']
    ten = stock[9]['name']
    eleven = stock[10]['name']
    twelve = stock[11]['name']
    thirteen = stock[12]['name']
    fourteen = stock[13]['name']
    fifteen = stock[14]['name']
    sixteen = stock[15]['name']
    seventeen = stock[16]['name']
    eighteen = stock[17]['name']
    nineteen = stock[18]['name']
    twenty = stock[19]['name']
    twentyone = stock[20]['name']
    twentytwo = stock[21]['name']
    twentythree = stock[22]['name']
    twentyfour = stock[23]['name']
    twentyfive = stock[24]['name']
    twentysix = stock[25]['name']
    twentyseven = stock[26]['name']
    twentyeight = stock[27]['name']
    twentynine = stock[28]['name']
    thirty = stock[29]['name']

    onedata = best_stock_list[0]
    twodata = best_stock_list[1]
    threedata = best_stock_list[2]
    fourdata = best_stock_list[3]
    fivedata = best_stock_list[4]
    sixdata = best_stock_list[5]
    sevendata = best_stock_list[6]
    eightdata = best_stock_list[7]
    ninedata = best_stock_list[8]
    tendata = best_stock_list[9]
    elevendata = best_stock_list[10]
    twelvedata = best_stock_list[11]
    thirteendata = best_stock_list[12]
    fourteendata = best_stock_list[13]
    fifteendata = best_stock_list[14]
    sixteendata = best_stock_list[15]
    seventeendata = best_stock_list[16]
    eighteendata = best_stock_list[17]
    nineteendata = best_stock_list[18]
    twentydata = best_stock_list[19]
    twentyonedata = best_stock_list[20]
    twentytwodata = best_stock_list[21]
    twentythreedata = best_stock_list[22]
    twentyfourdata = best_stock_list[23]
    twentyfivedata = best_stock_list[24]
    twentysixdata = best_stock_list[25]
    twentysevendata = best_stock_list[26]
    twentyeightdata = best_stock_list[27]
    twentyninedata = best_stock_list[28]
    thirtydata = best_stock_list[29]

    context = {
    'stock':stock,
    'best_stock_list':best_stock_list,
    'one':one,
    'two':two,
    'three':three,
    'four':four,
    'five':five,
    'six':six,
    'seven':seven,
    'eight':eight,
    'nine':nine,
    'ten':ten,
    'eleven':eleven,
    'twelve':twelve,
    'thirteen':thirteen,
    'fourteen':fourteen,
    'fifteen':fifteen,
    'sixteen':sixteen,
    'seventeen':seventeen,
    'eighteen':eighteen,
    'nineteen':nineteen,
    'twenty':twenty,
    'twentyone':twentyone,
    'twentytwo':twentytwo,
    'twentythree':twentythree,
    'twentyfour':twentyfour,
    'twentyfive':twentyfive,
    'twentysix':twentysix,
    'twentyseven':twentyseven,
    'twentyeight':twentyeight,
    'twentynine':twentynine,
    'thirty':thirty,
    'onedata':onedata,
    'twodata':twodata,
    'threedata':threedata,
    'fourdata':fourdata,
    'fivedata':fivedata,
    'sixdata':sixdata,
    'sevendata':sevendata,
    'eightdata':eightdata,
    'ninedata':ninedata,
    'tendata':tendata,
    'elevendata':elevendata,
    'twelvedata':twelvedata,
    'thirteendata':thirteendata,
    'fourteendata':fourteendata,
    'fifteendata':fifteendata,
    'sixteendata':sixteendata,
    'seventeendata':seventeendata,
    'eighteendata':eighteendata,
    'nineteendata':nineteendata,
    'twentydata':twentydata,
    'twentyonedata':twentyonedata,
    'twentytwodata':twentytwodata,
    'twentythreedata':twentythreedata,
    'twentyfourdata':twentyfourdata,
    'twentyfivedata':twentyfivedata,
    'twentysixdata':twentysixdata,
    'twentysevendata':twentysevendata,
    'twentyeightdata':twentyeightdata,
    'twentyninedata':twentyninedata,
    'thirtydata':thirtydata,
    }

    return render(request,template,context)

def worststocks(request):
    template = 'worststocks.html'
    stock = WorstStocks.objects.values()
    print(stock)
    best_stock_list = []
    for ticker in stock:
        symb = ticker['name']
        obj = get_object_or_404(StockInfo, name=symb)
        best_stock_list.append(obj)

    one = stock[0]['name']
    two = stock [1]['name']
    three = stock[2]['name']
    four = stock[3]['name']
    five = stock[4]['name']
    six = stock[5]['name']
    seven = stock[6]['name']
    eight = stock[7]['name']
    nine = stock[8]['name']
    ten = stock[9]['name']
    eleven = stock[10]['name']
    twelve = stock[11]['name']
    thirteen = stock[12]['name']
    fourteen = stock[13]['name']
    fifteen = stock[14]['name']
    sixteen = stock[15]['name']
    seventeen = stock[16]['name']
    eighteen = stock[17]['name']
    nineteen = stock[18]['name']
    twenty = stock[19]['name']
    twentyone = stock[20]['name']
    twentytwo = stock[21]['name']
    twentythree = stock[22]['name']
    twentyfour = stock[23]['name']
    twentyfive = stock[24]['name']
    twentysix = stock[25]['name']
    twentyseven = stock[26]['name']
    twentyeight = stock[27]['name']
    twentynine = stock[28]['name']
    thirty = stock[29]['name']

    onedata = best_stock_list[0]
    twodata = best_stock_list[1]
    threedata = best_stock_list[2]
    fourdata = best_stock_list[3]
    fivedata = best_stock_list[4]
    sixdata = best_stock_list[5]
    sevendata = best_stock_list[6]
    eightdata = best_stock_list[7]
    ninedata = best_stock_list[8]
    tendata = best_stock_list[9]
    elevendata = best_stock_list[10]
    twelvedata = best_stock_list[11]
    thirteendata = best_stock_list[12]
    fourteendata = best_stock_list[13]
    fifteendata = best_stock_list[14]
    sixteendata = best_stock_list[15]
    seventeendata = best_stock_list[16]
    eighteendata = best_stock_list[17]
    nineteendata = best_stock_list[18]
    twentydata = best_stock_list[19]
    twentyonedata = best_stock_list[20]
    twentytwodata = best_stock_list[21]
    twentythreedata = best_stock_list[22]
    twentyfourdata = best_stock_list[23]
    twentyfivedata = best_stock_list[24]
    twentysixdata = best_stock_list[25]
    twentysevendata = best_stock_list[26]
    twentyeightdata = best_stock_list[27]
    twentyninedata = best_stock_list[28]
    thirtydata = best_stock_list[29]

    context = {
    'stock':stock,
    'best_stock_list':best_stock_list,
    'one':one,
    'two':two,
    'three':three,
    'four':four,
    'five':five,
    'six':six,
    'seven':seven,
    'eight':eight,
    'nine':nine,
    'ten':ten,
    'eleven':eleven,
    'twelve':twelve,
    'thirteen':thirteen,
    'fourteen':fourteen,
    'fifteen':fifteen,
    'sixteen':sixteen,
    'seventeen':seventeen,
    'eighteen':eighteen,
    'nineteen':nineteen,
    'twenty':twenty,
    'twentyone':twentyone,
    'twentytwo':twentytwo,
    'twentythree':twentythree,
    'twentyfour':twentyfour,
    'twentyfive':twentyfive,
    'twentysix':twentysix,
    'twentyseven':twentyseven,
    'twentyeight':twentyeight,
    'twentynine':twentynine,
    'thirty':thirty,
    'onedata':onedata,
    'twodata':twodata,
    'threedata':threedata,
    'fourdata':fourdata,
    'fivedata':fivedata,
    'sixdata':sixdata,
    'sevendata':sevendata,
    'eightdata':eightdata,
    'ninedata':ninedata,
    'tendata':tendata,
    'elevendata':elevendata,
    'twelvedata':twelvedata,
    'thirteendata':thirteendata,
    'fourteendata':fourteendata,
    'fifteendata':fifteendata,
    'sixteendata':sixteendata,
    'seventeendata':seventeendata,
    'eighteendata':eighteendata,
    'nineteendata':nineteendata,
    'twentydata':twentydata,
    'twentyonedata':twentyonedata,
    'twentytwodata':twentytwodata,
    'twentythreedata':twentythreedata,
    'twentyfourdata':twentyfourdata,
    'twentyfivedata':twentyfivedata,
    'twentysixdata':twentysixdata,
    'twentysevendata':twentysevendata,
    'twentyeightdata':twentyeightdata,
    'twentyninedata':twentyninedata,
    'thirtydata':thirtydata,
    }

    return render(request,template,context)