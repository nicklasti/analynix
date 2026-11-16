"""Jobs that refresh the stock data. Run them through the management commands:

    python manage.py update_fundamentals   # finviz screener -> StockInfo
    python manage.py update_prices         # Yahoo Finance price history
    python manage.py grade_stocks          # recompute every grade (myapp/grading.py)
    python manage.py update_news           # finviz headlines
    python manage.py ai_analysis           # optional, needs OPENAI_API_KEY
    python manage.py update_all            # all of the above, in order
"""
