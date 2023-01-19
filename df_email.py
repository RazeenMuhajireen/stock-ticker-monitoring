import smtplib
import os
import pandas as pd
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()

gmail_user = os.environ.get('APP_MAIL_ADDRESS')
gmail_password = os.environ.get('MAIL_APP_PASSWORD')

sent_from = gmail_user
to = ['razeen.muhajireen@gmail.com']

msg = MIMEMultipart()
msg['Subject'] = "Stock Ticker Project - Daily Summary"
msg['From'] = gmail_user


data1 = {
    "TIcker Symbol": ['Google', 'Tesla'],
    "Last Update": ['date1', "date2"]
}
df1 = pd.DataFrame(data1)

html1 = """\
<html>
  <head>{0}</head>
  <body>
    {1}
  <br /><br /><br />
  </body>
</html>
""".format("Currently Live Stock Tickers", df1.to_html(index=False))
part1 = MIMEText(html1, 'html')


data2 = {
    "TIcker Symbol": ['Microsft', 'Apple'],
    "Last Update": ['date5', "date6"]
}
df2 = pd.DataFrame(data2)

html2 = """\
<html>
  <head>{0}</head>
  <body>
    {1}
  <br /><br /><br />
  </body>
</html>
""".format("Currently Dead Stock Tickers", df2.to_html(index=False))
part2 = MIMEText(html2, 'html')



data3 = {
    "x1": ["a", "b", "c"],
    "y2": [1,2,3]
}
df3 = pd.DataFrame(data3)
html3 = """\
<html>
  <head>{0}</head>
  <body>
    {1}
  <br /><br /><br />
  </body>
</html>
""".format("Stock Data Summary", df3.to_html(index=False))
part3 = MIMEText(html3, 'html')


msg.attach(part1)
msg.attach(part2)
msg.attach(part3)


try:
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.ehlo()
    smtp_server.login(gmail_user, gmail_password)
    smtp_server.sendmail(sent_from, to, msg.as_string())
    smtp_server.close()
    print("Email sent successfully!")
except Exception as ex:
    print("Something went wrong….", ex)

