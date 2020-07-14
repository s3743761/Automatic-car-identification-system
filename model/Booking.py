from flask import Flask, redirect, url_for, render_template, request, redirect, session, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from model.Car import Car
from model.User import User


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:iota2hd@35.197.179.42/Car'
db = SQLAlchemy(app)
app.secret_key = "hello"

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
    status = db.Column(db.String, default = "Processing")
    event_id = db.Column(db.String)

    def __repr__(self):
        return '<Booking %r>' % self.booking_id

    def book(self, car_id, username, duration):
        """
        Create a new booking with a certain duration
        """
        to_book = Car.query.get_or_404(car_id)
        time = int(duration)
        eventId = time
        print(eventId)
        new_booking = Booking(username=username, car_id=id, duration=duration, event_id=eventId)
        car_found = Car.query.filter_by(car_id = id).first()
        car_found.available = False
        db.session.add(new_booking)
        db.session.commit()

    def cancel(self, id):
        """
        cancel a booking, make the status of that booking to "Cancelled", make the car available to use
        """
        booking_to_cancel = Booking.query.get_or_404(id)
        booking_to_cancel.status = "Cancelled"
        car_found = Car.query.filter_by(car_id=booking_to_cancel.car_id).first()
        car_found.available = True
        db.session.commit()

    def finish(self, id):
        """
        Finalise a booking, make the status of the booking to "Finished", make the car available to use
        """
        car_to_finish = Car.query.filter_by(car_id=id).first()
        booking_to_finish = Booking.query.filter_by(car_id=id, finish=False).first()
        booking_to_finish.status = "Finished"
        car_to_finish.available = True
        db.session.commit()
