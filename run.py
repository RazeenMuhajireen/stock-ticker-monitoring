import os

from flask import redirect, url_for, jsonify, request
from flask_migrate import Migrate
from app.dataquery import testfunc

from app import create_app, db

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

app = create_app()
Migrate(app, db)

@app.route('/')
def hello():
    return "Hello world"

@app.route('/postdata', methods=['POST'])
def getdata():
    if request.method == 'POST':
        print("request is a post")
        field1 = request.args.get('field1')
        field2 = request.args.get('field2')
        print("args got ========")
        print(field1)
        print(field2)
        data = "Post sent"
        success = testfunc()
        return jsonify(data=data, success=success)



if __name__ == "__main__":
    app.run()


# check add_cron_job