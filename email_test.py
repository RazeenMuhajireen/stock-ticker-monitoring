import smtplib
import os
from dotenv import load_dotenv


load_dotenv()

gmail_user = os.environ.get('APP_MAIL_ADDRESS')
gmail_password = os.environ.get('MAIL_APP_PASSWORD')

sent_from = gmail_user
to = ['razeen.muhajireen@gmail.com']
subject = 'Send email now'
body = 'Test email'

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

try:
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.ehlo()
    smtp_server.login(gmail_user, gmail_password)
    smtp_server.sendmail(sent_from, to, email_text)
    smtp_server.close()
    print("Email sent successfully!")
except Exception as ex:
    print("Something went wrong….", ex)

