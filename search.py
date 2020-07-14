import speech_recognition as sr
from app import Car

#def main():

#def serchBrand(brand):

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