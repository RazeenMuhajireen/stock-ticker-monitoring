from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

app_gmail_address = os.environ.get('APP_MAIL_ADDRESS')
gmail_app_password = os.environ.get('MAIL_APP_PASSWORD')
to = ['addemailhere']

msg = MIMEMultipart()
msg['Subject'] = "Stock Ticker Project - Daily Summary"
msg['From'] = app_gmail_address


html1 = """
   <html>
     <head>test</head>
     <body>
     <br /><br /><br />
     </body>
   </html>
   """
part1 = MIMEText(html1, 'html')
msg.attach(part1)

try:
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.ehlo()
    smtp_server.login(app_gmail_address, gmail_app_password)
    smtp_server.sendmail(app_gmail_address, to, msg.as_string())
    smtp_server.close()
    print("Email sent successfully!")
except Exception as e:
    print("Failed to send email - " + str(e))