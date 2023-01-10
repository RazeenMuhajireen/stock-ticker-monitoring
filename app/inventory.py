from app import celery

@celery.task(ignore_result=True)
def fetch_stock_data():
    print("random task")


