from wtforms import Form, StringField, SelectField, validators, IntegerField, FloatField,PasswordField


class CarForm(Form):
    car_id = IntegerField('Car Id')
    brand = StringField('Brand')
    model = StringField('Model')
    locationX = FloatField('Location Start')
    locationY = FloatField('Location End')

class UserForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')
    firstname = StringField('Firstname')
    lastname = StringField('Lastname')
    email = StringField('Email')
    userType = StringField('User Type')
   

     
