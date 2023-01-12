import os

from flask import redirect, url_for, jsonify, request, current_app
from flask_migrate import Migrate
from app.dataquery import testfunc
from datetime import datetime
import celery
from celery.schedules import schedule
from app import create_app, db
from app import logger

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

app = create_app()
Migrate(app, db)

@app.route('/')
def hello():
    return "Hello world"

@app.route('/postdata', methods=['POST', 'GET'])
def getdata():
    if request.method == 'POST' or request.method == 'GET':
        print("request is a post")
        field1 = request.args.get('field1')
        field2 = request.args.get('field2')
        logger.warning("args got ========")
        logger.error("t1")
        logger.debug("x1")
        logger.critical("b1")
        print("change")

        print(field2)
        data = "Post sent"
        success = testfunc()
        return jsonify(data=data, success=success)

@app.route('/addtestjob', methods=['GET'])
def addtestjob():
    print("in new job add -------------")
    apredis = current_app.redis
    zentrytime =int(datetime.now().timestamp())
    cinterval = int(1) # be int
    cinterval = cinterval * 60
    croninterval = celery.schedules.schedule(run_every=cinterval)
    cfunction = 'app.inventory.fetch_stock_data'

    # customer = formdata[0]['customername']

    cargs1 = 'testargument'
    args = [cargs1]
    jobdescription = 'Minercontrol:Daily-RandomTask:' + 'TestTask'

    newjob = current_app.scheduler(jobdescription, cfunction, croninterval, args=args, app=current_app.celery)
    newjob.save()
    carglist = ','.join(args)
    newkey = '{}|{}|{}|{}'.format(jobdescription, croninterval, cfunction, carglist)
    apredis.zadd('cron_jobs', {newkey: zentrytime})
    return "test job added"


if __name__ == "__main__":
    app.run()


# check add_cron_job