from flask import current_app
from redbeat.decoder import RedBeatJSONDecoder
from app.models import TickerTable
from datetime import datetime
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
    elif searchitem == 'email':
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
            print("need to remove this job ===")
            print(job)
            apredis.zrem('cron_jobs', job)

    return 0, cronitem


def add_stock_info(stock_ticker_symbol, stock_name, description):
    stock_item = db.session.query(TickerTable).filter(TickerTable.tickersymbol == stock_ticker_symbol).first()

    if not stock_item:
        ticker_record = TickerTable(
            datestamp=datetime.utcnow(),
            tickersymbol=stock_ticker_symbol,
            stockname=stock_name,
            description=description,
            isalive=True
        )
        db.session.add(ticker_record)
        db.session.commit()
    else:
        if stock_item.isalive:
            print("already a job is running for this ")
        else:
            stock_item.isalive = True
            stock_item.stockname = stock_name
            stock_item.description = description
            db.session.commit()


def update_stock_info():
    print("edit stock info")