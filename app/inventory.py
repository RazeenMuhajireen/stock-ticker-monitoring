from app import celery

@celery.task(ignore_result=True)
def fetch_stock_data(testvariable):
    print("random task running now ---------------------" + testvariable)
    return "success"


@celery.task(ignore_result=True)
def send_email_summary():
    print("emai summary task running now ---------------------")
