from flask import Flask, render_template, request, redirect,url_for 
from src import db
from src.dtos import *

# Flask App definieren, static_folder auf public setzen
app = Flask(
    __name__
)
# app = Flask(
#     __name__,
#     template_folder="templates",
#     static_folder="static"
# )


# Startseite ausliefern
@app.route("/")
def default():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error=None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users:list[KontoinhaberDTO] = db.get_users()
        loged_in = False
        for user in users:
            print(user)
            if user.Email == email and user.Passwort == password:
                loged_in = True
                break
        if loged_in:
            return redirect(url_for("menue"))
        else:
            error = "E-Mail oder Passwort falsch"

    return render_template("login.html", error=error)

# Startseite ausliefern
@app.route("/registration")
def registration():
    return render_template("registration.html")


#Menue ausliefern
@app.route("/menue")
def menue():
    return render_template("menue.html")

# # Alle Benutzer abrufen
# @app.route("/api/users", methods=["GET"])
# def get_users():
#     pass

# # Benutzer hinzufügen
# @app.route("/api/users", methods=["POST"])
# def add_user():
#     pass

if __name__ == "__main__":
    
    app.run(host="127.0.0.1", port=3000, debug=True)
