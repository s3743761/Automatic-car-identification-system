from flask import Flask, redirect, url_for, Response,render_template, request, redirect, session, flash, Blueprint
#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.hash import sha256_crypt
from datetime import datetime
from datetime import timedelta
from flask_login import current_user
from googleapiclient.discovery import build
from forms import CarForm, UserForm
from httplib2 import Http
from oauth2client import file, client, tools
from flask_socketio import SocketIO, emit, send
from pymysql import NULL
from flask_googlemaps import GoogleMaps, Map
from pushbullet import Pushbullet
import speech_recognition as sr
import subprocess

#set up the google calendar
#SCOPES = "https://www.googleapis.com/auth/calendar"
store = file.Storage("token.json")
creds = store.get()
if(not creds or creds.invalid):
    flow = client.flow_from_clientsecrets("/Users/jakob/Desktop/IOT/Assignment3/PIoT_Assignment3/credentials.json", SCOPES)
    creds = tools.run_flow(flow, store)
service = build("calendar", "v3", http=creds.authorize(Http()))

#set up flask and sqlachemy
app = Flask(__name__)
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:iota2hd@35.197.179.42/Car'
db = SQLAlchemy(app)
#app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# set key as config
#app.config['GOOGLEMAPS_KEY'] = "AIzaSyC4j3ogRubmWzalYZIUmhuMUACtP_4vVG0"

# Initialize the extension
GoogleMaps(app)
pb = Pushbullet('o.rhD0Iy4jOrQvPtkEgd1muXHbvoLmGf19')

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
    status = db.Column(db.String, default = "Processing")
    event_id = db.Column(db.String)

    def __repr__(self):
        return '<Booking %r>' % self.booking_id

#Pages
@app.route("/", methods = ["POST", "GET"])
def login():
    """
    check the user typing information

    seacher the username and passport from User table

    also need verify the password

    if exit
    :return to the login page
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        username_found = User.query.filter_by(username=username).first()
        #result = User.query.filter_by(username=username).first()
        ##verify hash password
        if username_found:
                password_found = sha256_crypt.verify(password, username_found.password)
                if password_found:
                    username_session = username_found.username
                    session["username"] = username_session
                    if username_found.userType == "admin":
                        return render_template("adminBase.html",username = session["username"])
                    elif username_found.userType == "manager":
                        return render_template("managerBase.html",username = session["username"])
                    elif username_found.userType == "engineer":
                        return render_template("engineerBase.html",username = session["username"])
                    else:
                        return redirect(url_for("current"))
                else:
                    flash("password incorrect")
                    return render_template("login.html")
        else:
            flash("username not found")
            return render_template("login.html")
    else:       
        return render_template("login.html")

@app.route("/register", methods = ["POST", "GET"])
def register():
    """
    define a function hanlder the register html page in the MP pi
    implement the register function

    if user typing the correct information 
    register page pass the information to cloud database and save the information into database
    User table add a new User in the database

    :return a registration succesful message than return to the login html page

    if not 
    :return a fail registration message and return to the register page
    """
    if request.method == "POST":
        username = request.form.get('username')
        #hash password
        password = sha256_crypt.hash(request.form.get('password'))
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('EmailAddress')
        userType = request.form.get('userType')
        if username == "" or password == "" or firstname == "" or lastname == "" or email == "" or userType == "":
            flash("You must fill in everything!","error")
            return render_template("/register.html")
        elif User.query.filter_by(username=username).first():
            flash("User already exit! Please use other name! ")
            return render_template("/register.html")
        else:
            user = User(username=username, password=password, firstname=firstname, lastname=lastname, email=email, userType = userType)
            db.session.add(user)
            db.session.commit()
            flash("Your registration is successful!!","info")
            return redirect(url_for("login"))
    else:
        return render_template("/register.html")

@app.route("/logout")
def logout():
    """
    define a function to handler the logout button

    if user click logout button 

    then user logout the system

    :return to the home login page

    """
    flash("You have been logged out", "info")
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/current")
def current():
    """
    define a function to handler the current button

    do the research on the database

    select all the booked car detail by username

    :return all the booked car detail append this page
    
    """
    if "username" in session:
        usrname = session["username"]
        booking_found = Booking.query.filter_by(username = usrname).all()
        booking_current=[]
        for booking in booking_found:
            if booking.status == "Processing":
                booking_current.append(booking)
        return render_template("current.html", username = session["username"], currents = booking_current)
    else:
        flash("You must login first!","error")
        return redirect(url_for("login"))

@app.route("/cancel/<int:id>")
def cancel(id):
    """
    create a method to handler the cancel button

    list the booked car for the user

    cancle the current booked and also select that car by car_id 

    and cancel action system delect the booked car detail on cloud database

    at the same time, system hanlder the google calendar API and delete the event from google calendar

    event select by eventID that saved before
    """

    booking_to_cancel = Booking.query.get_or_404(id)

    try:
        booking_to_cancel.status = "Cancelled"
        car_found = Car.query.filter_by(car_id=booking_to_cancel.car_id).first()
        car_found.available = True
        db.session.commit()
        eventID = booking_to_cancel.event_id
        service.events().delete(calendarId='primary', eventId=eventID).execute()
        return redirect(url_for("current"))
    except:
        flash("There is a problem to cancel this booking!","error")
        return redirect(url_for("current"))

@app.route("/history")
def history():
    """
    create a method handler the history

    select booked car detail by username

    list all the booked car detail to user
    """
    if "username" in session:
        usrname = session["username"]
        booking_found = Booking.query.filter_by(username = usrname).all()
        return render_template("history.html", username = session["username"], hists = booking_found)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))

@app.route("/adminHistory")
def adminHistory():
    """
    create a method handler the history

    select booked car detail by username

    list all the booked car detail to user
    """
    if "username" in session:
        usrname = session["username"]
       
        # if usrname.userType == "admin":

        booking_found = Booking.query.all()
        return render_template("adminHistory.html", username = session["username"], hists = booking_found)
    

    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))


@app.route("/add", methods=['GET', 'POST'])
def add():

    if "username" in session:
        usrname = session["username"]  
        form = CarForm(request.form)
        if request.method == 'POST' and form.validate():
            car = Car()
            save_changes(car, form, new=True)
            flash('Car created successfully!')
            return render_template('adminBase.html', form = form)


        return render_template('addCar.html', form = form)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))

@app.route("/addUser", methods=['GET', 'POST'])
def addUser():

    if "username" in session:
        usrname = session["username"]  
        form = UserForm(request.form)
        if request.method == 'POST' and form.validate():
            user = User()
            save_changesUser(user, form, new=True)
            flash('User created successfully!')
            return render_template('adminBase.html', form = form)

        return render_template('addUser.html', form = form)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))

def save_changesUser(user, form, new=False):
   
    """
    Save the changes to the database
    """
    user.username = form.username.data
    user.password = sha256_crypt.hash(form.password.data)
    user.firstname = form.firstname.data
    user.lastname  = form.lastname.data
    user.email = form.email.data
    user.userType = form.userType.data

    if new:
        db.session.add(user)

    db.session.commit()
        
def save_changes(car, form, new=False):
   
    """
    Save the changes to the database
    """
    car.car_id = form.car_id.data
    car.brand = form.brand.data
    car.model = form.model.data
    car.locationX  = form.locationX.data
    car.locationY = form.locationY.data

    print(form.car_id.data)

    if new:
        db.session.add(car)

    db.session.commit()


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """
    edit a Car in the database
    """
    if "username" in session:
        usrname = session["username"]
        car = Car.query.filter(Car.car_id==id).first()
    
        if car:
            form = CarForm(formdata=request.form, obj=car)
            if request.method == 'POST' and form.validate():
            
                save_changes(car, form)
                flash('Car updated successfully!')
                return render_template('adminBase.html', form = form)
            return render_template('edit_car.html', form=form)
        else:
            return 'Error loading #{id}'.format(id=id)

@app.route('/editUser/<string:username>', methods=['GET', 'POST'])
def editUser(username):
    """
    edit a User in the database
    """
    if "username" in session:
        usrname = session["username"]
        user = User.query.filter(User.username == username).first()
    
        if user:
            form = UserForm(formdata=request.form, obj=user)
            if request.method == 'POST' and form.validate():
            
                save_changesUser(user, form)
                flash('User updated successfully!')
                return render_template('adminBase.html', form = form)
            return render_template('edit_user.html', form=form)
        else:
            return 'Error loading #{username}'.format(username = username)


@app.route("/cars")
def cars():
    """
    define a method list all the available car on web page

    select all the car that avaiable

    return a list of available cars
    """
    if "username" in session:
        usrname = session["username"]
        cars_found = Car.query.filter_by(available=True).all()
        return render_template("cars.html", username = session["username"], cars = cars_found)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))

@app.route("/all_car")
def all_cars():
    """
    define a method list all the cars on web page

    return a list of cars
    """
    if "username" in session:
        usrname = session["username"]
        cars_found = Car.query.all()
        return render_template("all_car.html", username = session["username"], cars = cars_found)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))

@app.route("/allReports")
def getAllReports():
   
    if "username" in session:
        usrname = session["username"]
        cars_found = Car.query.filter(Car.issues.isnot(None)).all()
        return render_template("allReports.html", username = session["username"], hists = cars_found)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))

@app.route("/search", methods=['GET', 'POST'])
def search():
    """
    implement the search function 

    that user could search by car_id, brand, or model

    system select the car table 

    :return a list of car that detail match the user type in

    """
    if "username" in session:
        usrname = session["username"]
        if request.method == "POST":
            search_word = request.form.get('searching')
            id_found = Car.query.filter_by(car_id=search_word).all()
            brand_found = Car.query.filter_by(brand=search_word).all()
            model_found = Car.query.filter_by(model=search_word).all()
            cars = []
            if id_found or brand_found or model_found:
                if id_found:
                    cars = id_found
                elif brand_found:
                    cars = brand_found
                else:
                    cars = model_found    
                return render_template("search.html", username=usrname, cars=cars)
            else:
                flash("No result found!","info")
                return render_template("search.html", username=usrname)
        else:
            flash("You have to enter some word to search!","error")
            return render_template("search.html", username=usrname)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))

@app.route("/adminSearch", methods=['GET', 'POST'])
def adminSearch():
    """
    implement the search function 

    that user could search by car_id, brand, or model

    system select the car table 

    :return a list of car that detail match the user type in

    """
    if "username" in session:
        usrname = session["username"]
        if request.method == "POST":
            search_word = request.form.get('searching')
            id_found = Car.query.filter_by(car_id=search_word).all()
            brand_found = Car.query.filter_by(brand=search_word).all()
            model_found = Car.query.filter_by(model=search_word).all()
            username_found = User.query.filter_by(username=search_word).all()
            cars = []
            users = []
            if id_found or brand_found or model_found:
                if id_found:
                    cars = id_found
                elif brand_found:
                    cars = brand_found
                else:
                    cars = model_found    
                return render_template("adminSearch.html", username=usrname, cars=cars)
            
            if username_found:
                users = username_found
                return render_template("adminSearch.html", username=usrname, users = users)

            else:
                flash("No result found!","info")
                return render_template("adminSearch.html", username=usrname)
        else:
            flash("You have to enter some word to search!","error")
            return render_template("adminSearch.html", username=usrname)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))

def Listening():
    MIC_NAME = "Microsoft® LifeCam HD-3000: USB Audio (hw:1,0)"

    # Set the device ID of the mic that we specifically want to use to avoid ambiguity
    for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
        if(microphone_name == MIC_NAME):
            device_id = i
            break

    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone(device_index = device_id) as source:
        # clear console of errors
        subprocess.run("clear")

        # wait for a second to let the recognizer adjust the
        # energy threshold based on the surrounding noise level
        r.adjust_for_ambient_noise(source)

        print("Say something!")
        try:
            audio = r.listen(source, timeout = 1.5)
        except sr.WaitTimeoutError:
            print("Listening timed out whilst waiting for phrase to start")
            quit()

    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        print("Google Speech Recognition thinks you said '{}'".format(r.recognize_google(audio)))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


@app.route("/delete/<int:id>", methods=['GET', 'POST'])
def delete(id):
    """
    method for handler the delete button on website

    admin can delete a car

    if deleted successful

    :return a deleted successful message and return to current page
    """

    car = Car.query.filter(Car.car_id == id).first()

    if car:
        
        if request.method == 'GET' :
            db.session.delete(car)
            db.session.commit()

            flash('Car deleted successfully!')
        return render_template('adminBase.html')
    else:
        return 'Error loading #{id}'.format(id=id)


@app.route("/deleteUser/<string:username>", methods=['GET', 'POST'])
def deleteUser(username):
    """
    method for handler the delete button on website

    admin can delete a car

    if deleted successful

    :return a deleted successful message and return to current page
    """

    user = User.query.filter(User.username == username).first()

    if user:
    
        if request.method == 'GET' :
            db.session.delete(user)
            db.session.commit()

            flash('User deleted successfully!')
        return render_template('adminBase.html')
    else:
        return 'Error loading #{username}'.format(username = username)

    
@app.route("/book/<int:id>", methods=['GET', 'POST'])
def book(id):
    """
    method for handler the book button on website

    user could book a car during the time that user want to use

    if book successful

    :return a booking successful message and return to current page
    """
    if "username" in session:
        usrname = session["username"]
        to_book = Car.query.get_or_404(id)
        if request.method == 'POST':
            duration_post = request.form['duration']
            if duration_post == "":
                flash("You must enter an duration", "error")
                return render_template("book.html", username=usrname, car = to_book)
            else:
                time = int(duration_post)
                eventId = insert(time)
                print(eventId)
                new_booking = Booking(username=usrname, car_id=id, duration=duration_post, event_id=eventId)
                car_found = Car.query.filter_by(car_id = id).first()
                car_found.available = False
                db.session.add(new_booking)
                db.session.commit()
                
                
                flash("Your booking is successful!", "info")
                return redirect(url_for("current"))
        else:
            return render_template("book.html", username=usrname, car = to_book)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))


@app.route("/report/<int:id>", methods=['GET', 'POST'])
def report(id):
    """
    method for handler the report button on admin website

    admin could report a car with issues to the engineer

    :return a reporting successful message and return to admin home page
    """
    if "username" in session:
        usrname = session["username"]
        to_report = Car.query.get_or_404(id)
        if request.method == 'POST':
            issue_post = request.form['issue']
            if issue_post == "":
                flash("You must enter an Issue", "error")
                return render_template("report.html", username=usrname, car = to_report)
            else:
               
                car_found = Car.query.filter_by(car_id = id).first()
                car_found.issues = issue_post
                car_found.available = False
                to_report = "Car Id: " + str(car_found.car_id) + "\nBrand: " + car_found.brand + "\nModel: " + car_found.model + "\nIssues: " + car_found.issues
                push = pb.push_note("A new car is reported by the admin!", to_report)
    
                db.session.commit()
            
                flash("You Have succesffuly Reported The Car !", "info")
                return render_template('adminBase.html')
        else:
            return render_template("report.html", username=usrname, car = to_report)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))

@app.route("/repair/<int:id>")
def repair(id):
    """
    Method to repair the reported cars.
    """

    car_to_repair = Car.query.get_or_404(id)

    try:
        car_to_repair.issues = None
        car_to_repair.available = True
        db.session.commit()
        return redirect(url_for("getAllReports"))
    except:
        flash("There is a problem to repair this car!","error")
        return redirect(url_for("getAllReports"))

def insert(time):
    """
    method for insert the event to user google calendar

    after booked a car calling this method and than insert event during the user book car time

    :return the eventID and save into the database for late if user want to delete this event

    """
    now = datetime.utcnow().isoformat() + "Z" 
    date = datetime.now()
    book = (date + timedelta(hours=time)).strftime("%Y-%m-%dT%H:%M:%S+10:00")
    time_start = date.strftime("%Y-%m-%dT%H:%M:%S+10:00").format()
    time_end = book.format()
    event = {
        "summary": "New Car Booking Event",
        "location": "RMIT Building 14",
        "description": "Adding New Car Booking Event",
        "start": {
            "dateTime": time_start,
            "timeZone": "Australia/Melbourne",
        },
        "end": {
            "dateTime": time_end,
            "timeZone": "Australia/Melbourne",
        },
        "attendees": [
            { "email": "jakobwei9@gmail.com" },
        ],
        "reminders": {
            "useDefault": False,
            "overrides": [
                { "method": "email", "minutes": 5 },
                { "method": "popup", "minutes": 10 },
            ],
        }
    }

    event = service.events().insert(calendarId ="primary", body = event).execute()
    eventId = event.get('id')
    return eventId
    ## store the eventID into the database

#socketio event handler

#when use img to log in 
def img_authenticate(imgname):
    """
    socketio event handler
    when use img to login
    """
    userimgname = User.query.filter_by(firstname=imgname).first()
    if imgname:
        return True

#when use password to log in 
def authenticate(username, password):
    """
    socketio event handler
    when use username and password to login
    """
    username_found = User.query.filter_by(username=username).first()
    ##verify hash password
    password_found = sha256_crypt.verify(password, username_found.password)
    if username_found and password_found:
        return True
    else:
        return False

def finishBook(carId):
    """
    this function for find list of car that user booked

    and after return change the car status
    """
    car_to_finish = Car.query.filter_by(car_id=carId).first()
    booking_to_finish = Booking.query.filter_by(car_id=carId, finish=False).first()
    booking_to_finish.status = "Finished"
    car_to_finish.available = True
    db.session.commit()
    eventID = booking_to_finish.event_id
    service.events().delete(calendarId='primary', eventId=eventID).execute()
    print('Succefully return the car!!')

def ack():
    print ('message was received!')

@socketio.on('identity')
def handle_my_custom_event(json):
    """
    handle the customer event by json
    """
    print('received json: ' + str(json))
    username = json['username']
    password = json['password']
    authenticate_pass = authenticate(username,password)
    if authenticate_pass == True:
        emit('validate', {'result' : 'success'}, callback=ack)
    else:
        emit('validate', {'result' : 'fail'}, callback=ack)

@socketio.on('name')
def handle_my_custom_event(json):
    """
    handle the customer event by json
    """
    print('received json: ' + str(json))
    imgname = json['imgname']
    authenticate_pass = img_authenticate(imgname)
    if authenticate_pass == True:
        emit('validate', {'result' : 'success'}, callback=ack)
    else:
        emit('validate', {'result' : 'fail'}, callback=ack)
@socketio.on('finish')
def handle_finish(json):
    car_id = json['car_id']
    finishBook(car_id)
    emit('my response', {'result': 'Return succeed!'})

@socketio.on('connect')
def test_connect():
    """
    that just for return a message when connected
    """
    print('Client connected')
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    """
    that just for return a message when disconnected
    """
    print('Client disconnected')

def updateNumOfBrand():
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

@app.route('/bar')
def bar():
    update = updateNumOfBrand()
    bar_labels = update[0]
    bar_values= update[1]
    return render_template('bar_chart.html', title='Number of Car Brand Booked', max=30, labels=bar_labels, values=bar_values)

@app.route('/line')
def line():
    update = updateNumOfBrand()
    line_labels = update[0]
    line_values = update[1]
    return render_template('line_chart.html', title='Number of Car Brand Booked', max=30, labels=line_labels, values=line_values)

@app.route('/pie')
def pie():
    update = updateNumOfBrand()
    pie_labels = update[0]
    pie_values = update[1]
    colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA", "#ABCDEF", "#DDDDDD", "#ABCABC"]
    return render_template('pie_chart.html', title='Number of Car Brand Booked', max=30, set=zip(pie_values, pie_labels, colors))

#Google map
@app.route("/map")
def mapview():
    if "username" in session:
        usrname = session["username"]
        cars_found = Car.query.filter(Car.issues.isnot(None)).all()
        carMarkers = list()
        for car in cars_found:
            carMarker = {
                'icon': 'http://maps.google.com/mapfiles/kml/pal4/icon15.png',
                'lat':  car.locationY,
                'lng':  car.locationX,
                'infobox': "Car Id: " + str(car.car_id) + 
                           " Brand: " + car.brand +
                           " Model: " + car.model +
                           " Issues: " + car.issues
            }
            carMarkers.append(carMarker)
        sndmap = Map(
        identifier = "sndmap",
        lat =  37.4419 ,
        lng =  -122.1419 ,
        markers = carMarkers,
        fit_markers_to_bounds = True,
        style="height:600px;width:1000px;margin:0;"
        )
        return render_template('map.html', sndmap=sndmap)
    else:
        flash("You must login first!","info")
        return redirect(url_for("login"))
    # creating a map in the view
    


if __name__ == "__main__":
    socketio.run(app, debug = True)
