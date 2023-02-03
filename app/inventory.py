import smtplib
import os
import yfinance as yf
from app import create_app
from app.models import StockDataTable, TickerTable
from app.dataquery import get_summary_data
from app import celery, db, logger
from datetime import datetime
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


load_dotenv()

# Try to load the app once
app = create_app()
celery.conf.update(app.config)
app.app_context().push()


@celery.task(ignore_result=True)
def fetch_stock_data(ticker_symbol):
    # celery task for fetching data from yfinance for ticker symbol
    try:
        ticker_item = db.session.query(TickerTable).filter(TickerTable.tickersymbol == str(ticker_symbol)).first()
        if ticker_item:
            basic_info = yf.Ticker(ticker_symbol).basic_info
            info = yf.Ticker(ticker_symbol).info

            stockdatapoint = StockDataTable(
                datestamp=datetime.utcnow(),
                sector=str(info['sector']),
                country=str(info['country']),
                regularMarketOpen=str(basic_info['open']),
                regularMarketPrice=str(basic_info['last_price']),
                regularMarketPreviousClose=str(basic_info['previous_close']),
                regularMarketVolume=str(basic_info['last_volume']),
                regularMarketDayLow=str(basic_info['day_low']),
                regularMarketDayHigh=str(basic_info['day_high']),
                marketCap=str(basic_info['market_cap'])
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
    # celery task for sending email summary
    app_gmail_address = os.environ.get('APP_MAIL_ADDRESS')
    gmail_app_password = os.environ.get('MAIL_APP_PASSWORD')
    to = [email_id]

    msg = MIMEMultipart()
    msg['Subject'] = "Stock Ticker Project - Daily Summary"
    msg['From'] = app_gmail_address

    running_df, dead_df = get_summary_data()

    if len(running_df) > 0:
        html1 = """\
        <html>
          <head>{0}</head>
          <body>
            {1}
          <br /><br /><br />
          </body>
        </html>
        """.format("Currently Live Stock Tickers", running_df.to_html(index=False))
        part1 = MIMEText(html1, 'html')
        msg.attach(part1)

    if len(dead_df) > 0:
        html2 = """\
        <html>
          <head>{0}</head>
          <body>
            {1}
          <br /><br /><br />
          </body>
        </html>
        """.format("Currently Dead Stock Tickers", dead_df.to_html(index=False))
        part2 = MIMEText(html2, 'html')
        msg.attach(part2)

    try:
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.starttls()
        smtp_server.ehlo()
        smtp_server.login(app_gmail_address, gmail_app_password)
        smtp_server.sendmail(app_gmail_address, to, msg.as_string())
        smtp_server.close()
        logger.debug("Email sent successfully!")
    except Exception as e:
        logger.error("Failed to send email - " + str(e))
