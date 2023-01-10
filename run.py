import os

from flask import redirect, url_for
from flask_migrate import Migrate

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


if __name__ == "__main__":
    app.run()
