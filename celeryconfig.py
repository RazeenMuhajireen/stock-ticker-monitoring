from kombu import Exchange, Queue
from dotenv import load_dotenv
import os

load_dotenv()

broker_url = os.environ.get('CELERY_BROKER_URL')
beat_scheduler = os.environ.get('BEAT_SCHEDULER')
beat_max_loop_interval = 5
REDBEAT_LOCK_TIMEOUT = beat_max_loop_interval * 5
task_queues = (
    Queue('normal', Exchange('normal'), routing_key='normal'),
    Queue('low', Exchange('low'), routing_key='low'),
)

task_default_queue = 'normal'
task_default_exchange = 'normal'

task_default_routing_key = 'normal'
task_routes = {
    'app.inventory.fetch_stock_data': {'queue': 'normal'},
    'app.inventory.send_email_summary': {'queue': 'normal'}
}

