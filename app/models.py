from app import db
from datetime import datetime

class TickerTable(db.Model):
    # After 30 days the performance data gets rotated here
    __tablename__ = 'tickertable'

    id = db.Column(db.Integer, primary_key=True)
    datestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    tickersymbol = db.Column(db.String(40))
    stockname = db.Column(db.String(40), server_default='None', default='None')
    description = db.Column(db.String(40), server_default='None', default='None')