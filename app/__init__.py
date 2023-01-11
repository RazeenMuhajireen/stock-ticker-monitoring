from dotenv import load_dotenv
from celery import Celery
from flask import Flask
from redis import Redis
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()

db = SQLAlchemy()

celery = Celery(__name__,
                broker=os.environ.get('CELERY_BROKER_URL'),
                backend=os.environ.get('CELERY_BROKER_URL'))
celery.config_from_object('celeryconfig')

def register_env_variables(app):
    app.debug = os.environ.get('DEBUG', 'False') == 'True'

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')

    app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL')

def create_app():
    app = Flask(__name__)
    print("creating app")
    register_env_variables(app)
    app.redis = Redis.from_url(os.environ.get('REDIS_URL'))
    return app