from flask import Flask, redirect, url_for, render_template, request, redirect, session, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from model.Car import Car
from model.Booking import Booking

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Manager(User,db.Model):
    super()

    def updateNumOfBrand():
        '''
        Return a list of brand and their corresponding number of bookings
        '''
        #For the visualisation dashboard
        labels = [
        'BMW', 'Benz', 'Telsla', 'Mazda',
        'Toyota', 'Honda', 'Maruti' ]
        #find the number of each brand in all bookings
        bmw = 0
        benz = 0
        telsla = 0
        mazda = 0
        toyota = 0
        honda = 0
        maruti = 0
        bookings = Booking.query.all()
        for booking in bookings:
            id = booking.car_id
            car = Car.query.filter_by(car_id = id).first()
            if car != None:
                if car.brand == "BMW":
                    bmw = bmw + 1
                if car.brand == "Benz":
                    benz = benz + 1
                if car.brand == "Telsla":
                    telsla = telsla + 1
                if car.brand == "Mazda":
                    mazda = mazda + 1
                if car.brand == "Toyota":
                    toyota = toyota + 1
                if car.brand == "Honda":
                    honda = honda + 1
                if car.brand == "Maruti":
                    maruti = maruti + 1
        values = [bmw, benz, telsla, mazda, toyota, honda, maruti]
        return labels, values