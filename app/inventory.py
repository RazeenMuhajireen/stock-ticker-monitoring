from app import celery, db
import yfinance as yf
from app.models import StockDataTable, TickerTable
from datetime import datetime


@celery.task(ignore_result=True)
def fetch_stock_data(ticker_symbol):
    print("collecting now ---------------------" + ticker_symbol)

    ticker_item = db.session.query(TickerTable).filter(TickerTable.tickersymbol == ticker_symbol).first()

    ticker = yf.Ticker(ticker_symbol).info

    stockdatapoint = StockDataTable(
        datestamp=datetime.utcnow(),
        sector=str(ticker['sector']),
        country=str(ticker['country']),
        market_price=str(ticker['market_price']),
        previous_close_price=str(ticker['previous_close_price']),
        regularMarketOpen=str(ticker['regularMarketOpen']),
        regularMarketPrice=str(ticker['regularMarketPrice']),
        regularMarketPreviousClose=str(ticker['regularMarketPreviousClose']),
        regularMarketVolume=str(ticker['regularMarketVolume']),
        regularMarketDayLow=str(ticker['regularMarketDayLow']),
        regularMarketDayHigh=str(ticker['regularMarketDayHigh']),
        marketCap=str(ticker['marketCap'])
    )
    ticker_item.stock_data.append(stockdatapoint)
    db.session.add(stockdatapoint)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return "success"


@celery.task(ignore_result=True)
def send_email_summary():
    print("email summary task running now ---------------------")
