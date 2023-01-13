from app import celery

@celery.task(ignore_result=True)
def fetch_stock_data(ticker_symbol):
    print("collecting now ---------------------" + ticker_symbol)

    # pull data from yfinance and store to db -----------------------------------------------------------
    return "success"


@celery.task(ignore_result=True)
def send_email_summary():
    print("email summary task running now ---------------------")
