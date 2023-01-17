from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, desc
from app import create_app
from datetime import datetime
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

app = create_app()
app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)


class TickerTable(db.Model):
    __tablename__ = 'stocktickertable'

    id = db.Column(db.Integer, primary_key=True)
    datestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    tickersymbol = db.Column(db.String(40))
    stockname = db.Column(db.String(40), server_default='None', default='None')
    description = db.Column(db.String(40), server_default='None', default='None')
    isalive = db.Column(db.Boolean, default=True)
    stock_data = db.relationship('StockDataTable', backref=db.backref('stockdataticker', lazy=True))


class StockDataTable(db.Model):
    __tablename__ = 'stockdatatable'

    id = db.Column(db.Integer, primary_key=True)
    datestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    sector = db.Column(db.String(100))
    country = db.Column(db.String(100))
    regularMarketOpen = db.Column(db.String(100))
    regularMarketPrice = db.Column(db.String(100))
    regularMarketPreviousClose = db.Column(db.String(100))
    regularMarketVolume = db.Column(db.String(100))
    regularMarketDayLow = db.Column(db.String(100))
    regularMarketDayHigh = db.Column(db.String(100))
    marketCap = db.Column(db.String(100))
    stock_ticker_id = db.Column(Integer, db.ForeignKey('stocktickertable.id'))


class EmailID(db.Model):
    __tablename__ = 'emailid'

    id = db.Column(db.Integer, primary_key=True)
    emai_id = db.Column(db.String(100))
    dailymail_flag = db.Column(db.Boolean, default=False)
    isalive = db.Column(db.Boolean, default=True)


running_df = pd.DataFrame()
dead_df = pd.DataFrame()

running_tickers = db.session.query(TickerTable).filter(TickerTable.isalive == True).all()
if len(running_tickers) > 0:
    running_data_list = []
    for i in range(len(running_tickers)):
        data = {}
        data['Ticker Symbol'] = running_tickers[i].tickersymbol
        data['Stock Name'] = running_tickers[i].stockname
        data['Description'] = running_tickers[i].description
        data['Last Update'] = running_tickers[i].datestamp
        data['Market Price'] = "Unknown"
        data['Market Volume'] = "Unknown"
        marketdata = db.session.query(StockDataTable)\
            .filter(StockDataTable.stock_ticker_id == running_tickers[i].id)\
            .order_by(desc(StockDataTable.datestamp)).first()
        if marketdata:
            data['Last Update'] = marketdata.datestamp
            data['Market Price'] = marketdata.regularMarketPrice
            data['Market Volume'] = marketdata.regularMarketVolume
        running_data_list.append(data)
    if len(running_data_list) > 0:
        running_df = pd.DataFrame(running_data_list)

dead_tickers = db.session.query(TickerTable).filter(TickerTable.isalive == False).all()
if len(dead_tickers) > 0:
    dead_data_list = []
    for i in range(len(dead_tickers)):
        data = {}
        data['Ticker Symbol'] = dead_tickers[i].tickersymbol
        data['Stock Name'] = dead_tickers[i].stockname
        data['Description'] = dead_tickers[i].description
        data['Last Update'] = dead_tickers[i].datestamp
        data['Market Price'] = "Unknown"
        data['Market Volume'] = "Unknown"
        marketdata = db.session.query(StockDataTable)\
            .filter(StockDataTable.stock_ticker_id == dead_tickers[i].id)\
            .order_by(desc(StockDataTable.datestamp)).first()
        if marketdata:
            data['Last Update'] = marketdata.datestamp
            data['Market Price'] = marketdata.regularMarketPrice
            data['Market Volume'] = marketdata.regularMarketVolume
        dead_data_list.append(data)
    if len(dead_data_list) > 0:
        dead_df = pd.DataFrame(dead_data_list)



