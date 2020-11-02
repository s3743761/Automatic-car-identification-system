from flask import Flask, redirect, url_for, render_template, request, redirect, session, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from model.Car import Car
from model.Booking import Booking

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Engineer(User,db.Model):
    super()

    def fetchAllReports(self):
        """
        Get all the reported car from the databse
        """
        cars_found = Car.query.filter(Car.issues.isnot(None)).all()
        return cars_found

    def repair(self, id):
        """
        Repair a car, making the issues to None and making the car to available
        """
        car_to_repair = Car.query.get_or_404(id)
        car_to_repair.issues = None
        car_to_repair.available = True
        db.session.commit()