import os
from flask import redirect, url_for, jsonify, request, current_app
from flask_migrate import Migrate
from app.dataquery import remove_job, search_cron_job
from datetime import datetime
import celery
from app import create_app, db
from app import logger
from app.models import TickerTable, StockDataTable

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

app = create_app()
Migrate(app, db)

@app.route('/')
def hello():
    return "Hello world"

@app.route('/add_job', methods=['POST'])
def add_ticker_job():
    print("in new job add -------------")
    apredis = current_app.redis
    zentrytime = int(datetime.now().timestamp())

    cinterval = int(request.args.get('interval'))
    cjobtype = request.args.get('job_type')

    cinterval = cinterval * 60
    croninterval = celery.schedules.schedule(run_every=cinterval)

    if cjobtype == "inventory":
        cfunction = 'app.inventory.fetch_stock_data'
        cargs1 = request.args.get('stock_ticker_symbol')
        cargs2 = request.args.get('stock_name')
        cargs3 = request.args.get('description')

        # store the description and combo data to sql table stock_tickers -------------------------
        # check if already this ticker symbol is available before creating new record -----------------

        args = [cargs1]
        jobdescription = 'StockTicker:inventory:' + str(cargs1)
    elif cjobtype == "dailymail":
        cfunction = 'app.inventory.send_email_summary'
        cargs1 = request.args.get('email_address')
        args = [cargs1]
        jobdescription = 'StockTicker:dailyemail:' + str(cargs1)

    newjob = current_app.scheduler(jobdescription, cfunction, croninterval, args=args, app=current_app.celery)
    newjob.save()
    carglist = ','.join(args)
    newkey = '{}|{}|{}|{}'.format(jobdescription, croninterval, cfunction, carglist)
    apredis.zadd('cron_jobs', {newkey: zentrytime})
    data = "Job added successfully"
    # logger.warning("args got ========")
    # logger.error("t1")
    # logger.debug("x1")
    # logger.critical("b1")
    return jsonify(data=data, success="True")


@app.route('/remove_scheduled_job', methods=['POST'])
def remove_scheduled_job():
    jobtype = request.args.get('job_type')
    term = request.args.get('term')
    jobs = search_cron_job(term, jobtype)
    print(jobs)
    message = remove_job(jobs[1][0][0])
    return message


@app.route('/list_jobs', methods=['GET'])
def list_jobs():
    jobtype = request.args.get('job_type', 'all')
    term = request.args.get('term', '')
    jobs = search_cron_job(term, jobtype)
    # combine these data with the description stuff from db ==========================================
    print(jobs)
    return "done"


@app.route('/update_stock_details', methods=['GET', "POST"])
def update_stock_details():
    ticker_symbol = request.args.get('ticker_symbol', '')
    description = request.args.get('description', '')
    stock_name = request.args.get('stock_name', '')
    # update stock name and description in DB ====================================================
    # do not allow to change ticker symbol
    print("update function nned work")
    return "update done"


@app.route('/single_stock_data', methods=['GET'])
def single_stock_data():
    # Retrieve a single stock along with its market stats. alive or dead---------show status---------------------
    print("done")

@app.route('/all_stock_data', methods=['GET'])
def all_stock_data():
    # args live, all, dead status stock data--------------------show status--------------------------
    # show market stats too-------------------------
    print("ok")

if __name__ == "__main__":
    app.run()