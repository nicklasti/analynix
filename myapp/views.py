from django.shortcuts import render
from django.http import HttpResponse
import yfinance as yf
from urllib.request import Request, urlopen
import re


def index(request):
    return render(request, 'index.html')
    # renders the index


def overview(request):

    text = request.GET['text']
    # pulls the ticker from the index.html form

    stock = yf.Ticker(text)
    # assigns the yf stock ticker interpreter function to a variable

    ticker = stock.info['symbol']
    # gets the ticker

    companyName = stock.info['longName']
    # gets the company name

    industry = stock.info['sector']
    # gets the SECTOR

    beta = round(stock.info['beta'], 2)
    # gets the beta

    mktCap = stock.info['marketCap']
    # gets the market cap

    if len(str(mktCap)) == 15:
        mktCapD = str(str(round(float(mktCap), -9))
                      [:3])+'.'+str(str(round(float(mktCap), -9))[3:5]+'T')
    if len(str(mktCap)) == 14:
        mktCapD = str(str(round(float(mktCap), -9))
                      [:2])+'.'+str(str(round(float(mktCap), -9))[2:4]+'T')
    if len(str(mktCap)) == 13:
        mktCapD = str(str(round(float(mktCap), -9))
                      [:1])+'.'+str(str(round(float(mktCap), -9))[1:3]+'T')
    elif len(str(mktCap)) == 12:
        mktCapD = str(str(round(float(mktCap), -7))
                      [:3])+'.'+str(str(round(float(mktCap), -7))[3:5]+'B')
    elif len(str(mktCap)) == 11:
        mktCapD = str(str(round(float(mktCap), -7))
                      [:2])+'.'+str(str(round(float(mktCap), -7))[2:4]+'B')
    elif len(str(mktCap)) == 10:
        mktCapD = str(str(round(float(mktCap), -7))
                      [:1])+'.'+str(str(round(float(mktCap), -7))[1:3]+'B')
    elif len(str(mktCap)) == 9:
        mktCapD = str(str(round(float(mktCap), -4))
                      [:3])+'.'+str(str(round(float(mktCap), -4))[3:5]+'M')
    elif len(str(mktCap)) == 8:
        mktCapD = str(str(round(float(mktCap), -4))
                      [:2])+'.'+str(str(round(float(mktCap), -4))[2:4]+'M')
    elif len(str(mktCap)) == 7:
        mktCapD = str(str(round(float(mktCap), -4))
                      [:1])+'.'+str(str(round(float(mktCap), -4))[1:3]+'M')
    elif len(str(mktCap)) < 7:
        mktCapD = (format(int(mktCap), ',d'))
    # formats short number mil bil tril for market cap

    bookValue = stock.info['bookValue']*stock.info['sharesOutstanding']
    # gets the book value

    revenue = stock.info['totalRevenue']
    # gets the sales

    profit = stock.info['netIncomeToCommon']
    # gets the net income

    profitMargin = profit/revenue
    # gets the PM

    profitMarginD = round(profitMargin, 2)
    # formats the PM

    revGrwth = stock.info['revenueGrowth']
    revGrwthD = round(float(revGrwth), 5)
    revGrwthD = str(revGrwthD)
    revGrwthD = (revGrwthD[2:4] + '.' + revGrwthD[4:6] + '%')
    # gets revenue growth

    req = Request('https://finviz.com/quote.ashx?t='+ticker,
                  headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read().decode('utf-8')
    content = re.findall(
        '(?<=class="tab-link").*?(?=</a>)', webpage, re.DOTALL)
    sector = content[2]
    sector = sector[1:]
    sector = sector.strip()
    # gets the sector

    req2 = Request('https://finviz.com/groups.ashx?g=industry&v=120&o=name',
                   headers={'User-Agent': 'Mozilla/5.0'})
    webpage2 = urlopen(req2).read().decode('utf-8')
    indSize = re.findall(
        '(?<='+sector+').*?(?=class="body-table")(.*?)(?=</td>)', webpage2, re.DOTALL)
    indSize = re.findall('[0-9.]+.', str(indSize))
    indSize = re.sub(r"\['(.*)'\]", r"\1", str(indSize))
    # gets the industry market cap for display

    indSizeFloat = float(indSize[:-1])*1000000000
    # gets the industry market cap as a float

    sector2 = sector.lower()
    sector2 = sector2.replace(" ", "")
    sector2 = sector2.replace("&","")
    sector2 = sector2.replace("-", "")
    req3 = Request('https://finviz.com/screener.ashx?f=ind_' +
                   sector2+'&v=121', headers={'User-Agent': 'Mozilla/5.0'})
    webpage3 = urlopen(req3).read().decode('utf-8')
    sectorCount = re.findall(
        '(?<=<b>Total: </b>).*?(?=#)', webpage3, re.DOTALL)
    sectorCount = re.findall('[0-9.]+.', str(sectorCount))
    sectorCount = re.sub(r"\['(.*)'\]", r"\1", str(sectorCount))
    sectorCount = float(sectorCount)
    # counts how many companies are listed in that sector

    avgCapFloat = indSizeFloat / sectorCount
    # gets the average industry market cap float

    avgCapInt = re.findall('([0-9].*)\.', str(avgCapFloat))
    # gets rid of the decimal place numbers

    avgCap = re.sub(r"\['(.*)'\]", r"\1", str(avgCapInt))
    # gets rid of ['']

    if len(str(avgCap)) == 15:
        avgCap = str(str(round(float(avgCap), -9))
                     [:3])+'.'+str(str(round(float(avgCap), -9))[3:5]+'T')
    if len(str(avgCap)) == 14:
        avgCap = str(str(round(float(avgCap), -9))
                     [:2])+'.'+str(str(round(float(avgCap), -9))[2:4]+'T')
    if len(str(avgCap)) == 13:
        avgCap = str(str(round(float(avgCap), -9))
                     [:1])+'.'+str(str(round(float(avgCap), -9))[1:3]+'T')
    elif len(str(avgCap)) == 12:
        avgCap = str(str(round(float(avgCap), -7))
                     [:3])+'.'+str(str(round(float(avgCap), -7))[3:5]+'B')
    elif len(str(avgCap)) == 11:
        avgCap = str(str(round(float(avgCap), -7))
                     [:2])+'.'+str(str(round(float(avgCap), -7))[2:4]+'B')
    elif len(str(avgCap)) == 10:
        avgCap = str(str(round(float(avgCap), -7))
                     [:1])+'.'+str(str(round(float(avgCap), -7))[1:3]+'B')
    elif len(str(avgCap)) == 9:
        avgCap = str(str(round(float(avgCap), -4))
                     [:3])+'.'+str(str(round(float(avgCap), -4))[3:5]+'M')
    elif len(str(avgCap)) == 8:
        avgCap = str(str(round(float(avgCap), -4))
                     [:2])+'.'+str(str(round(float(avgCap), -4))[2:4]+'M')
    elif len(str(avgCap)) == 7:
        avgCap = str(str(round(float(avgCap), -4))
                     [:1])+'.'+str(str(round(float(avgCap), -4))[1:3]+'M')
    elif len(str(avgCap)) < 7:
        avgCap = (format(int(avgCap), ',d'))
    # formats short number mil bil tril for industry average market cap

    mktCapFloat = float(mktCap)
    # market cap float

    mktShareFloat = mktCapFloat / indSizeFloat
    # market share float

    if len(indSize) >= 8:
        indSize = str(str(round(indSizeFloat, -10))
                      [:1]+'.'+str(round(indSizeFloat, -10))[1:3]+'T')
    elif len(indSize) < 8:
        indSize = indSize
    # fixes trillions

    mktSharePct = re.findall('[0-9].+', str(mktShareFloat))
    mktSharePct = re.sub(r"\['(.*)'\]", r"\1", str(mktSharePct))
    mktSharePct = round(float(mktSharePct), 5)
    mktSharePct = str(mktSharePct)
    mktSharePct = (mktSharePct[2:4] + '.' + mktSharePct[4:6] + '%')
    # for display

    if len(str(revenue)) == 15:
        revenueD = str(str(round(float(revenue), -9))
                       [:3])+'.'+str(str(round(float(revenue), -9))[3:5]+'T')
    if len(str(revenue)) == 14:
        revenueD = str(str(round(float(revenue), -9))
                       [:2])+'.'+str(str(round(float(revenue), -9))[2:4]+'T')
    if len(str(revenue)) == 13:
        revenueD = str(str(round(float(revenue), -9))
                       [:1])+'.'+str(str(round(float(avgCap), -9))[1:3]+'T')
    elif len(str(revenue)) == 12:
        revenueD = str(str(round(float(revenue), -7))
                       [:3])+'.'+str(str(round(float(revenue), -7))[3:5]+'B')
    elif len(str(revenue)) == 11:
        revenueD = str(str(round(float(revenue), -7))
                       [:2])+'.'+str(str(round(float(revenue), -7))[2:4]+'B')
    elif len(str(revenue)) == 10:
        revenueD = str(str(round(float(revenue), -7))
                       [:1])+'.'+str(str(round(float(revenue), -7))[1:3]+'B')
    elif len(str(revenue)) == 9:
        revenueD = str(str(round(float(revenue), -4))
                       [:3])+'.'+str(str(round(float(revenue), -4))[3:5]+'M')
    elif len(str(revenue)) == 8:
        revenueD = str(str(round(float(revenue), -4))
                       [:2])+'.'+str(str(round(float(revenue), -4))[2:4]+'M')
    elif len(str(revenue)) == 7:
        revenueD = str(str(round(float(revenue), -4))
                       [:1])+'.'+str(str(round(float(revenue), -4))[1:3]+'M')
    elif len(str(revenue)) < 7:
        revenueD = (format(int(revenue), ',d'))
    # formats sales

    if len(str(profit)) == 15:
        profitD = str(str(round(float(profit), -9))
                      [:3])+'.'+str(str(round(float(profit), -9))[3:5]+'T')
    if len(str(profit)) == 14:
        profitD = str(str(round(float(profit), -9))
                      [:2])+'.'+str(str(round(float(profit), -9))[2:4]+'T')
    if len(str(profit)) == 13:
        profitD = str(str(round(float(profit), -9))
                      [:1])+'.'+str(str(round(float(avgCap), -9))[1:3]+'T')
    elif len(str(profit)) == 12:
        profitD = str(str(round(float(profit), -7))
                      [:3])+'.'+str(str(round(float(profit), -7))[3:5]+'B')
    elif len(str(profit)) == 11:
        profitD = str(str(round(float(profit), -7))
                      [:2])+'.'+str(str(round(float(profit), -7))[2:4]+'B')
    elif len(str(profit)) == 10:
        profitD = str(str(round(float(profit), -7))
                      [:1])+'.'+str(str(round(float(profit), -7))[1:3]+'B')
    elif len(str(profit)) == 9:
        profitD = str(str(round(float(profit), -4))
                      [:3])+'.'+str(str(round(float(profit), -4))[3:5]+'M')
    elif len(str(profit)) == 8:
        profitD = str(str(round(float(profit), -4))
                      [:2])+'.'+str(str(round(float(profit), -4))[2:4]+'M')
    elif len(str(profit)) == 7:
        profitD = str(str(round(float(profit), -4))
                      [:1])+'.'+str(str(round(float(profit), -4))[1:3]+'M')
    elif len(str(profit)) < 7:
        profitD = (format(int(profit), ',d'))
    
    # formats net income

    return render(request, 'overview.html', {'companyName': companyName, 'ticker': ticker, 'industry': industry, 'beta': beta, 'mktCapD': mktCapD, 'bookValue': bookValue, 'revenueD': revenueD, 'profitD': profitD, 'sector': sector, 'indSize': indSize, 'mktSharePct': mktSharePct, 'avgCap': avgCap, 'profitMarginD':  profitMarginD, 'revGrwthD': revGrwthD})
