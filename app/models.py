from app import db
from datetime import datetime
from sqlalchemy import Integer

class TickerTable(db.Model):
    __tablename__ = 'stocktickertable'

    id = db.Column(db.Integer, primary_key=True)
    datestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    tickersymbol = db.Column(db.String(40))
    stockname = db.Column(db.String(40), server_default='None', default='None')
    description = db.Column(db.String(40), server_default='None', default='None')
    alive = db.Column(db.Boolean, default=True)
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