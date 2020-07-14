from flask import Flask, redirect, url_for, render_template, request, redirect, session, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:iota2hd@35.197.179.42/Car'
db = SQLAlchemy(app)
app.secret_key = "hello"

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

    def AddCar(self, id, brand, model, X, Y, available, issues):
        """
        Add a new car into the database
        """
        car = Car(car_id=id, brand=brand, model=model, locationX=X, locationY=Y, available=available, issues=issues)

        db.session.add(car)
        db.session.commit()

    def editCar(self, id, brand, model, X, Y, available, issues):
        """
        Edit the infomations of a given car
        """
        self.car_id = id
        self.brand = brand
        self.model = model
        self.locationX = X
        self.locationY = Y
        self.available = available
        self.issues = issues

        db.session.commit()
    
    def deleteCar(self):
        """
        delete a car from the database
        """
        db.session.delete(self)
        db.session.commit()