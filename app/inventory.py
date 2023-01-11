from app import celery

@celery.task(ignore_result=True)
def fetch_stock_data():
    print("random task running now ---------------------")


@celery.task(ignore_result=True)
def send_email_summary():
    print("emai summary task running now ---------------------")
