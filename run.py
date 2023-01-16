import os
from flask import redirect, url_for, jsonify, request, current_app
from flask_migrate import Migrate
from app.dataquery import remove_job, search_cron_job, add_stock_info, update_ticker_info, add_daily_email_info
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
def add_job():
    apredis = current_app.redis
    zentrytime = int(datetime.now().timestamp())

    if 'interval' not in request.args:
        data = "'interval' parameter missing. please specify interval as integer."
        return jsonify(data=data, success=False)
    if 'job_type' not in request.args:
        data = "'job_type' parameter missing. please specify job_type as inventory or dailyemail."
        return jsonify(data=data, success=False)

    cinterval = int(request.args.get('interval'))
    cjobtype = request.args.get('job_type')

    cinterval = cinterval * 60
    croninterval = celery.schedules.schedule(run_every=cinterval)

    if cjobtype == "inventory":
        cfunction = 'app.inventory.fetch_stock_data'
        if 'stock_ticker_symbol' not in request.args:
            data = "'stock_ticker_symbol' parameter missing. please specify stock_ticker_symbol."
            return jsonify(data=data, success=False)
        cargs1 = request.args.get('stock_ticker_symbol')
        cargs2 = request.args.get('stock_name', "Not Set")
        cargs3 = request.args.get('description', "Not Set")

        add_ticker_result = add_stock_info(cargs1, cargs2, cargs3)

        if not add_ticker_result[0]:
            data = "Unable to add job. Ticker job already running for the ticker symbol:" + str(cargs1)
            return jsonify(data=data, success=False)
        args = [cargs1]
        jobdescription = 'StockTicker:inventory:' + str(cargs1)

    elif cjobtype == "dailyemail":
        cfunction = 'app.inventory.send_email_summary'
        if 'email_address' not in request.args:
            data = "'email_address' parameter missing. please specify email address to send summary mail."
            return jsonify(data=data, success=False)

        cargs1 = request.args.get('email_address')
        args = [cargs1]
        jobdescription = 'StockTicker:dailyemail:' + str(cargs1)

        add_email_result = add_daily_email_info(cargs1)
        if not add_email_result[0]:
            data = "Unable to add job. Email job already running for the email address:" + str(cargs1)
            return jsonify(data=data, success=False)

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
    return jsonify(data=data, success=True)


@app.route('/remove_scheduled_job', methods=['POST'])
def remove_scheduled_job():
    if 'job_type' not in request.args:
        data = "'job_type' parameter missing. please specify as inventory or dailyemail."
        return jsonify(data=data, success=False)
    if 'term' not in request.args:
        data = "'term' parameter missing. plaese specify term as stock ticker symbol for inventory job or email " \
               "address for dailyemail job"
        return jsonify(data=data, success=False)
    jobtype = request.args.get('job_type')
    term = request.args.get('term')
    jobs = search_cron_job(term, jobtype)
    print(jobs)
    if len(jobs[1]) > 0:
        message = remove_job(jobs[1][0][0])
    else:
        message = "No matching job to remove"
    return jsonify(data=message, success=True)


@app.route('/list_jobs', methods=['GET'])
def list_jobs():
    jobtype = request.args.get('job_type', 'all')
    term = request.args.get('term', '')
    jobs = search_cron_job(term, jobtype)
    # combine these data with the description stuff from db ==========================================
    print(jobs)
    return "done"


@app.route('/update_ticker_details', methods=['GET', "POST"])
def update_ticker_details():
    ticker_symbol = request.args.get('ticker_symbol', '')
    stock_name = request.args.get('stock_name', '')
    description = request.args.get('description', '')

    result = update_ticker_info(ticker_symbol, stock_name, description)

    return jsonify(data=result[1], success=result[0])


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