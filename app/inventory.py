
import yfinance as yf
from app import create_app
from app.models import StockDataTable, TickerTable, EmailID
from app import celery, db, logger
from datetime import datetime
from dotenv import load_dotenv
import smtplib
import os

load_dotenv()

# Try to load the app once
app = create_app()
celery.conf.update(app.config)
app.app_context().push()


@celery.task(ignore_result=True)
def fetch_stock_data(ticker_symbol):
    try:
        ticker_item = db.session.query(TickerTable).filter(TickerTable.tickersymbol == str(ticker_symbol)).first()
        ticker = yf.Ticker(ticker_symbol).info
        print(ticker)

        stockdatapoint = StockDataTable(
            datestamp=datetime.utcnow(),
            sector=str(ticker['sector']),
            country=str(ticker['country']),
            regularMarketOpen=str(ticker['regularMarketOpen']),
            regularMarketPrice=str(ticker['regularMarketPrice']),
            regularMarketPreviousClose=str(ticker['regularMarketPreviousClose']),
            regularMarketVolume=str(ticker['regularMarketVolume']),
            regularMarketDayLow=str(ticker['regularMarketDayLow']),
            regularMarketDayHigh=str(ticker['regularMarketDayHigh']),
            marketCap=str(ticker['marketCap'])
        )
        ticker_item.stock_data.append(stockdatapoint)
        db.session.add(stockdatapoint)
        db.session.commit()
    except Exception as e:
        logger.error("Error in ticker job: " + str(e))
        db.session.rollback()
    return "success"


@celery.task(ignore_result=True)
def send_email_summary(email_id):
    print("email id -------------- " + str(email_id))
    print("email summary task running now ---------------------")
    app_gmail_address = os.environ.get('APP_MAIL_ADDRESS')
    gmail_app_password = os.environ.get('MAIL_APP_PASSWORD')

    subject = 'Daily Summary Report - Stock Monitoring App - '
    body = 'Change this email body................'

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (app_gmail_address, email_id, subject, body)

    try:
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)

        smtp_server.starttls()
        smtp_server.ehlo()

        smtp_server.login(app_gmail_address, gmail_app_password)
        smtp_server.sendmail(app_gmail_address, email_id, email_text)
        smtp_server.close()
        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong….", ex)
