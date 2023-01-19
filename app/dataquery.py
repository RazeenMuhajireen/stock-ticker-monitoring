import pandas as pd
import json
from flask import current_app
from redbeat.decoder import RedBeatJSONDecoder
from app.models import TickerTable, EmailID, StockDataTable
from datetime import datetime
from sqlalchemy import desc
from app import db, logger


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
        try:
            db.session.commit()
            return True, "created new ticker entry"
        except Exception as e:
            db.session.rollback()
            logger.error("unable to create")
            return False, "failed to create new ticker entry"
    else:
        if ticker_item.isalive:
            return False, "ticker already exists and running."
        else:
            ticker_item.isalive = True
            ticker_item.stockname = stock_name
            ticker_item.description = description
            try:
                db.session.commit()
                return True, "ticker already exists, updated info and running again."
            except Exception as e:
                db.session.rollback()
                logger.error("unable to update ticker info")
                return True, "ticker already exists, update info failed, but running job again."


def update_ticker_info(ticker_id, stock_name, description):
    ticker_item = db.session.query(TickerTable).filter(TickerTable.id == ticker_id).first()

    if ticker_item:
        if stock_name:
            ticker_item.stockname = stock_name
        if description:
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

        try:
            db.session.add(email_record)
            db.session.commit()
            return True, "created new email entry"
        except Exception as e:
            db.session.rollback()
            logger.error("failed to create new email " + str(e))
            return False, "failed to create new email entry."
    else:
        if email_item.isalive:
            if email_item.dailymail_flag:
                return False, "daily summary email already exists and running."
            else:
                email_item.dailymail_flag = True
                try:
                    db.session.commit()
                    return True, "email already exists, setting daily summary email."
                except Exception as e:
                    db.session.rollback()
                    logger.error("failed to update email flag")
                    return False, 'failed to update email flag'

        else:
            email_item.isalive = True
            email_item.dailymail_flag = True
            try:
                db.session.commit()
                return True, "email already exists, setting daily summary email."
            except Exception as e:
                db.session.rollback()
                return False, "failed to change email flags"


def update_dailyemail_status(emailid):
    emailitem = db.session.query(EmailID).filter(EmailID.emai_id == emailid).first()
    if emailitem:
        emailitem.dailymail_flag = False
        emailitem.isalive = False
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()


def update_ticker_status(ticker_symbol):
    ticker_object = db.session.query(TickerTable).filter(TickerTable.tickersymbol == ticker_symbol).first()
    if ticker_object:
        ticker_object.isalive = False
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("failed to change status of ticker" + str(e))


def list_all_current_stock_data():
    results = []
    running_ticker_jobs = db.session.query(TickerTable).filter(TickerTable.isalive == True).all()
    if len(running_ticker_jobs) > 0:
        for ticker_item in running_ticker_jobs:
            marketdict = {}
            marketdict['ticker_id'] = ticker_item.id
            marketdict['ticker_symbol'] = ticker_item.tickersymbol
            marketdict['stock_name'] = ticker_item.stockname
            marketdict['description'] = ticker_item.description
            marketdata = db.session.query(StockDataTable) \
                .filter(StockDataTable.stock_ticker_id == ticker_item.id)\
                .order_by(desc(StockDataTable.datestamp)).first()
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


def get_stock_data(ticker_id):
    results = []
    stock_data = db.session.query(TickerTable, StockDataTable)\
        .join(StockDataTable)\
        .filter(TickerTable.id == ticker_id).all()
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


def get_summary_data():
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
            marketdata = db.session.query(StockDataTable) \
                .filter(StockDataTable.stock_ticker_id == running_tickers[i].id) \
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
            marketdata = db.session.query(StockDataTable) \
                .filter(StockDataTable.stock_ticker_id == dead_tickers[i].id) \
                .order_by(desc(StockDataTable.datestamp)).first()
            if marketdata:
                data['Last Update'] = marketdata.datestamp
                data['Market Price'] = marketdata.regularMarketPrice
                data['Market Volume'] = marketdata.regularMarketVolume
            dead_data_list.append(data)
        if len(dead_data_list) > 0:
            dead_df = pd.DataFrame(dead_data_list)
    return running_df, dead_df


def get_tickers_info():
    results = []
    all_tickers = db.session.query(TickerTable).all()
    if all_tickers:
        for ticker in all_tickers:
            data = {}
            data['id'] = ticker.id
            data['date_created'] = ticker.datestamp
            data['ticker_symbol'] = ticker.tickersymbol
            data['stockname'] = ticker.stockname
            data['description'] = ticker.description
            data['isalive'] = ticker.isalive
            results.append(data)
    return results


