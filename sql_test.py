from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()
app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)


class Person(db.Model):
    # This is a table used to track whether the pool configuration is applied to device
    __tablename__ = 'Persons'
    PersonID = db.Column(db.Integer, primary_key=True)
    LastName = db.Column(db.String(100), nullable=False, server_default='')
    FirstName = db.Column(db.String(100), nullable=False, server_default='')
    Address = db.Column(db.String(100), nullable=False, server_default='')
    City = db.Column(db.String(100), nullable=False, server_default='')


# newnetry = Person(PersonID=1,
#                   LastName="Muhajireen",
#                   FirstName="Razeen",
#                   Address="Test address",
#                   City="Test City")
# db.session.add(newnetry)
# db.session.commit()
data = db.session.query(Person).all()
print(data)

