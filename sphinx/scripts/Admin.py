from flask import Flask, redirect, url_for, render_template, request, redirect, session, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from model.User import User
from model.Car import Car
from model.Booking import Booking



class Admain(User,db.Model):
    super()
    '''
    this is admin class
    '''
    def fetchAllCars(self):
        """
        get all the cars in the database depite they're available or not
        """
        cars_found = Car.query.all()
        return cars_found

    def addUser(self, username, password, firstname, lastname, email):
        """
        add a new user into the database
        """
        
        user = User(username = username, password = password, firstname = firstname, lastname = lastname, email = email)

    

        return user

    def getAllUsers(self):
        """
        get the all the user information from database

        return a list of user

        """
        result = User.query.all()

        return result 

    def editUser(self, user, username, password, firstname, lastname, email):
        """
        edit an user's information by passing the information wants to change
        """
        user.username = username
        user.password = password
        user.firstname = firstname
        user.lastname = lastname
        user.email = email 

        

    def rmCar(self, car):
        """
        remove a car from database
        """
        car.deleteCar()

    def rmUser(self, user):
        """
        remove an user from the database
        """
        user.deleteUser()

    def report(self, carId, issues):
        """
        report a car with issues to the engineer, make it unavailable to use
        """
        car_found = Car.query.filter_by(car_id = carId).first()
        car_found.issues = issues
        car_found.available = False

      

        
        
