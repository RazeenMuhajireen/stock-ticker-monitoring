import os
from flask import jsonify, request, current_app
from flask_migrate import Migrate
from app.dataquery import remove_job, search_cron_job, add_ticker_info, update_ticker_info, add_daily_email_info, \
    update_dailyemail_status, update_ticker_status, list_all_current_stock_data, get_stock_data, get_tickers_info
from datetime import datetime
import celery
import json
from app import create_app, db
from app import logger


# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

app = create_app()
Migrate(app, db)


@app.route('/add_job', methods=['POST'])
def add_job():
    apredis = current_app.redis
    zentrytime = int(datetime.now().timestamp())

    json_data = json.loads(request.data)

    cjobtype = json_data.get('job_type', None)

    # if interval is not specified default interval is 15 minutes
    cinterval = int(json_data.get('interval', '15'))
    cinterval = cinterval * 60
    croninterval = celery.schedules.schedule(run_every=cinterval)

    if cjobtype:
        if cjobtype == 'inventory':
            stock_ticker_symbol = json_data.get('stock_ticker_symbol', None)
            stock_name = json_data.get('stock_name', 'Not Set')
            description = json_data.get('description', 'Not Set')
            if not stock_ticker_symbol:
                data = "Key missing. 'stock_ticker_symbol'."
                return jsonify(data=data, success=False)
            else:
                cfunction = 'app.inventory.fetch_stock_data'
                add_ticker_result = add_ticker_info(stock_ticker_symbol, stock_name, description)
                if not add_ticker_result[0]:
                    data = "Unable to add job. Ticker job already running for the ticker symbol:" + str(stock_ticker_symbol)
                    return jsonify(data=data, success=False)
                args = [stock_ticker_symbol]
                jobdescription = 'StockTicker:inventory:' + str(stock_ticker_symbol)

        else:
            # job_type == 'dailyemail
            email_address = json_data.get('email_address', None)
            if not email_address:
                data = "Key missing. 'email_address'."
                return jsonify(data=data, success=False)
            else:
                cfunction = 'app.inventory.send_email_summary'
                add_email_result = add_daily_email_info(email_address)
                if not add_email_result[0]:
                    data = "Unable to add job. Email job already running for the email address:" + str(email_address)
                    return jsonify(data=data, success=False)
                args = [email_address]
                jobdescription = 'StockTicker:dailyemail:' + str(email_address)

    else:
        data = "Key missing. 'job_type'."
        return jsonify(data=data, success=False)

    newjob = current_app.scheduler(jobdescription, cfunction, croninterval, args=args, app=current_app.celery)
    newjob.save()
    carglist = ','.join(args)
    newkey = '{}|{}|{}|{}'.format(jobdescription, croninterval, cfunction, carglist)
    apredis.zadd('cron_jobs', {newkey: zentrytime})
    data = "Job added successfully"
    return jsonify(data=data, success=True)


@app.route('/remove_scheduled_job', methods=['POST'])
def remove_scheduled_job():
    json_data = json.loads(request.data)
    jobtype = json_data.get('job_type', None)
    term =  json_data.get('term', None)

    if jobtype is None:
        data = "Key missing. 'job_type'. please specify job_type as 'inventory' or 'dailyemail'."
        return jsonify(data=data, success=False)
    if term is None:
        data = "Key missing. 'term'. please specify term as stock ticker symbol for inventory job or email address " \
               "for dailyemail job"
        return jsonify(data=data, success=False)

    jobs = search_cron_job(term, jobtype)
    if len(jobs[1]) > 0:
        message = remove_job(jobs[1][0][0])
        if jobtype == 'dailyemail':
            update_dailyemail_status(term)
        elif jobtype == 'inventory':
            update_ticker_status(term)
    else:
        message = "No matching job to remove"
    return jsonify(data=message, success=True)


@app.route('/list_current_stock_jobs', methods=['GET'])
def list_current_stock_jobs():
    data = list_all_current_stock_data()
    return jsonify(data=data, success=True)


@app.route('/update_ticker_details/<ticker_id>', methods=['POST'])
def update_ticker_details(ticker_id):
    json_data = json.loads(request.data)
    stock_name = json_data.get('stock_name', None)
    description = json_data.get('description', None)

    result = update_ticker_info(ticker_id, stock_name, description)

    return jsonify(data=result[1], success=result[0])


@app.route('/single_stock_data/<ticker_id>', methods=['GET'])
def single_stock_data(ticker_id):
    data = get_stock_data(ticker_id)
    return jsonify(data=data, success=True)


@app.route('/list_all_tickers_info', methods=['GET'])
def list_all_tickers_info():
    data = get_tickers_info()
    return jsonify(data=data, success=True)


if __name__ == "__main__":
    app.run()
