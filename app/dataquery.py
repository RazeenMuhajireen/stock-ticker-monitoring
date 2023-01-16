from flask import current_app
from redbeat.decoder import RedBeatJSONDecoder
from app.models import TickerTable, EmailID, StockDataTable
from datetime import datetime
from sqlalchemy import desc
from app import db
import pandas as pd
import json


def search_cron_job(term, searchitem):
    r = current_app.redis
    namelist = []
    schedulelist = []
    tasklist = []
    argslist = []

    if term == '':
        term = '*'
    else:
        term = term + '*'

    if searchitem == 'all':
        scantype = 'redbeat:StockTicker:'
    elif searchitem == 'inventory':
        scantype = 'redbeat:StockTicker:inventory:'
    elif searchitem == 'dailyemail':
        scantype = 'redbeat:StockTicker:dailyemail:'
    else:
        scantype = ''

    print(scantype + term)
    for key in r.scan_iter(scantype + term):
        keyvalue = r.hget(key, 'definition')
        decodedkey = json.loads(keyvalue, cls=RedBeatJSONDecoder)
        namelist.append(decodedkey['name'])
        schedulelist.append(decodedkey['schedule'])
        tasklist.append(decodedkey['task'])

        sublist = []
        if decodedkey['args']:
            for i in range(len(decodedkey['args'])):
                sublist.append(str(decodedkey['args'][i]))
            newargslist = ','.join(sublist)
            argslist.append(newargslist)
        else:
            argslist.append('None')
    items = list(zip(namelist, schedulelist, tasklist, argslist))
    df = pd.DataFrame(items, columns=['namelist', 'scheulelist', 'tasklist', 'arglist'])
    sorteddf = df.sort_values("tasklist").sort_values('arglist')
    namelist = sorteddf['namelist'].tolist()
    schedulelist = sorteddf['scheulelist'].tolist()
    tasklist = sorteddf['tasklist'].tolist()
    argslist = sorteddf['arglist'].tolist()
    items = list(zip(namelist, schedulelist, tasklist, argslist))

    return 0, items


def remove_job(cronitem):
    print("cron item to delete ====")
    print(cronitem)
    entry = current_app.scheduler(cronitem, app=current_app.celery)
    entry.delete()

    apredis = current_app.redis

    cron_jobs = apredis.zrange('cron_jobs', 0, -1)
    for job in cron_jobs:
        split = job.split('|')

        if cronitem in split[0]:
            apredis.zrem('cron_jobs', job)

    return 'job removed successfully.'


def add_ticker_info(stock_ticker_symbol, stock_name, description):
    ticker_item = db.session.query(TickerTable).filter(TickerTable.tickersymbol == stock_ticker_symbol).first()

    if not ticker_item:
        ticker_record = TickerTable(
            datestamp=datetime.utcnow(),
            tickersymbol=stock_ticker_symbol,
            stockname=stock_name,
            description=description,
            isalive=True
        )
        db.session.add(ticker_record)
        db.session.commit()
        return True, "created new ticker entry"
    else:
        if ticker_item.isalive:
            return False, "ticker already exists and running."
        else:
            ticker_item.isalive = True
            ticker_item.stockname = stock_name
            ticker_item.description = description
            db.session.commit()
            return True, "ticker already exists, updated info and running again."


def update_ticker_info(stock_ticker_symbol, stock_name, description):
    ticker_item = db.session.query(TickerTable).filter(TickerTable.tickersymbol == stock_ticker_symbol).first()

    if ticker_item:
        if stock_name != '':
            ticker_item.stockname = stock_name
        if description != '':
            ticker_item.description = description
        try:
            db.session.commit()
            return True, "stock ticker info updated successfully."
        except Exception as e:
            db.session.rollback()
            return False, "Unable to update ticker info:" + str(e)
    else:
        return False, "No ticker item found."


def add_daily_email_info(email_id):
    email_item = db.session.query(EmailID).filter(EmailID.emai_id == email_id).first()

    if not email_item:
        email_record = EmailID(
            emai_id=str(email_id),
            dailymail_flag=True,
            isalive=True
        )
        db.session.add(email_record)
        db.session.commit()
        return True, "created new email entry"
    else:
        if email_item.isalive:
            if email_item.dailymail_flag:
                return False, "daily summary email already exists and running."
            else:
                email_item.dailymail_flag = True
                db.session.commit()
                return True, "email already exists, setting daily summary email."

        else:
            email_item.isalive = True
            email_item.dailymail_flag = True
            db.session.commit()
            return True, "email already exists, setting daily summary email."


def update_dailyemail_status(emailid):
    emailitem = db.session.query(EmailID).filter(EmailID.emai_id == emailid).first()
    if emailitem:
        emailitem.dailymail_flag = False
        emailitem.isalive = False
        db.session.commit()


def update_ticker_status(ticker_symbol):
    ticker_object = db.session.query(TickerTable).filter(TickerTable.tickersymbol == ticker_symbol).first()
    if ticker_object:
        ticker_object.isalive = False
        db.session.commit()


def list_all_current_stock_data():
    results = []
    running_ticker_jobs = db.session.query(TickerTable).filter(TickerTable.isalive == True).all()
    if len(running_ticker_jobs) > 0:
        for ticker_item in running_ticker_jobs:
            marketdict = {}
            marketdict['ticker_symbol'] = ticker_item.tickersymbol
            marketdict['stock_name'] = ticker_item.stockname
            marketdict['description'] = ticker_item.description
            marketdata = db.session.query(StockDataTable) \
                .filter(StockDataTable.stock_ticker_id == ticker_item.id).order_by(
                desc(StockDataTable.datestamp)).first()
            marketdict['sector'] = marketdata.sector
            marketdict['country'] = marketdata.country
            marketdict['regularMarketOpen'] = marketdata.regularMarketOpen
            marketdict['regularMarketPrice'] = marketdata.regularMarketPrice
            marketdict['regularMarketPreviousClose'] = marketdata.regularMarketPreviousClose
            marketdict['regularMarketDayLow'] = marketdata.regularMarketDayLow
            marketdict['regularMarketDayHigh'] = marketdata.regularMarketDayHigh
            marketdict['marketCap'] = marketdata.marketCap
            marketdict['datestamp'] = marketdata.datestamp
            marketdict['regularMarketVolume'] = marketdata.regularMarketVolume
            results.append(marketdict)
    return results


def get_stock_data(ticker_symbol):
    results = []
    stock_data = db.session.query(TickerTable, StockDataTable)\
        .join(StockDataTable)\
        .filter(TickerTable.tickersymbol == ticker_symbol).all()
    if len(stock_data) > 0:
        for datapoint in stock_data:
            marketdict = {}
            marketdict['ticker_symbol'] = datapoint.TickerTable.tickersymbol
            marketdict['stock_name'] = datapoint.TickerTable.stockname
            marketdict['description'] = datapoint.TickerTable.description
            marketdict['isalive'] = datapoint.TickerTable.isalive
            marketdict['sector'] = datapoint.StockDataTable.sector
            marketdict['country'] = datapoint.StockDataTable.country
            marketdict['regularMarketOpen'] = datapoint.StockDataTable.regularMarketOpen
            marketdict['regularMarketPrice'] = datapoint.StockDataTable.regularMarketPrice
            marketdict['regularMarketPreviousClose'] = datapoint.StockDataTable.regularMarketPreviousClose
            marketdict['regularMarketDayLow'] = datapoint.StockDataTable.regularMarketDayLow
            marketdict['regularMarketDayHigh'] = datapoint.StockDataTable.regularMarketDayHigh
            marketdict['marketCap'] = datapoint.StockDataTable.marketCap
            marketdict['datestamp'] = datapoint.StockDataTable.datestamp
            marketdict['regularMarketVolume'] = datapoint.StockDataTable.regularMarketVolume
            results.append(marketdict)

    return results
