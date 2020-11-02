from flask import Flask, redirect, url_for, render_template, request, redirect, session, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from model.Car import Car
from model.Booking import Booking

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    """
    User class for create a data type for user register and save data on cloud.
    """
    username = db.Column(db.String(90), primary_key=True)
    password = db.Column(db.String(80))
    firstname = db.Column(db.String(120))
    lastname = db.Column(db.String(120))
    email = db.Column( db.String(100))

    def __init__(self, username, password, firstname, lastname, email):
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.email = email

    def fetchAvailableCars(self):
        """
        get a list of available cars
        """
        cars_found = Car.query.filter_by(available=True).all()
        return cars_found

    def fetchCurrentBookings(self, usrname):
        """
        Get the current bookings processing of this user
        """
        booking_found = Booking.query.filter_by(username = usrname).all()
        booking_current=[]
        for booking in booking_found:
            if booking.status == "Processing":
                booking_current.append(booking)
        return booking_current

    def fetchAllBookings(self, usrname):
        """
        get all the bookings of this user
        """
        booking_found = Booking.query.filter_by(username = usrname).all()
        return booking_found

    def deleteUser(self):
        """
        delete an user from the database
        """
        db.session.delete(self)
        db.session.commit()
    