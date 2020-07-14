from flask import Flask, redirect, url_for, render_template, request, redirect, session, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:iota2hd@35.197.179.42/Car'
db = SQLAlchemy(app)

"""
create the database for the whole project

create table User for users

table Car for car details

table booking for booking car 
"""
#models 
class User(db.Model):
    """
    User class for create a data type for user register and save data on cloud.
    """
    username = db.Column(db.String(90), primary_key=True)
    password = db.Column(db.String(80))
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    email = db.Column( db.String(100))
    userType = db.Column( db.String(100))
    
    def __repr__(self):
        return '<User %r>' % self.username

class Car(db.Model):
    """
    Car clsss for create a data type for car entity and save the data on cloud.
    """
    car_id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    locationX = db.Column(db.Float)
    locationY = db.Column(db.Float)
    available = db.Column(db.Boolean, default=True)
    issues = db.Column( db.String(400))


    def __repr__(self):
        return '<Car %r>' % self.car_id
    
class Booking(db.Model):
    """
    Booking class for keep a booking handler and get the google calendar event ID for the 
    booking action. after booking save the event ID on cloud. and then could select the event ID
    basic book ID return or delete google calendar event
    """
    booking_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(90))
    car_id = db.Column(db.Integer)
    time = db.Column(db.DateTime, default = datetime.now)
    duration = db.Column(db.Integer)
    status = db.Column(db.String(100), default = "Processing")
    event_id = db.Column(db.String(100))

    def __repr__(self):
        return '<Booking %r>' % self.booking_id
'''
Just use code below to add new data into the database

'''


#user = User(username="s1234", password="s1234", firstname="David", lastname="Jones", email="sdff@wedwe", userType="admin")
#booking = Booking(username="s1234", car_id=10,duration=360, event_id="sedwaefewsrar34frer")
car = Car(brand="Maruti",model='SB3', locationX =898923, locationY= 47671)
db.create_all()
db.session.add(car)
db.session.commit()
