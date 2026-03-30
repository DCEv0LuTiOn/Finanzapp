from flask import Flask, render_template, request, redirect,url_for, session
from functools import wraps  # sorgt dafür, dass die Route ihren echten Namen behält für decorator benötigt
import db
from dtos import *

# Flask App definieren, static_folder auf public setzen
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)
app.secret_key = "supersecretkey"  # wichtig für session das diese sicher ist
# app = Flask(
#     __name__,
#     template_folder="templates",
#     static_folder="static"
# )



# Decorator
def login_required(route_function):  # das ist die Funktion (Route), die geschützt werden soll
    @wraps(route_function)  # wichtig damit Flask die Route korrekt erkennt
    def wrapper_function(*args, **kwargs):  
        # *args = alle normalen Positionswerte (z.B. /user/5 → 5 wird hier reingepackt)
        #        → wird als Liste/Tupel weitergegeben, ohne Namen
        #
        # **kwargs = alle benannten Werte (z.B. /user?id=5 oder Flask-Parameter wie id=5)
        #          → wird als Wörterbuch (dict) weitergegeben: {"id": 5}
        #
        # Flask nutzt das automatisch, damit deine Funktion alles bekommt was die Route erwartet

        if "user_id" not in session:  # prüfen: ist der User NICHT eingeloggt?
            return redirect(url_for("login"))  # wenn nein → weiter zur Login-Seite

        return route_function(*args, **kwargs)  # wenn ja → ursprüngliche Route mit allen Daten ausführen

    return wrapper_function  # gibt die geschützte Funktion zurück

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
                session["user_id"] = user.ID  # Session sicher machen userid in session speichern
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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


#Menue ausliefern
@app.route("/menue")
@login_required
def menue():
    return render_template("menue.html")

#Menue ausliefern
@app.route("/data_input")
@login_required
def data_input():
    return render_template("data_input.html")

#Menue ausliefern
@app.route("/data_edit")
@login_required
def data_edit():
    return render_template("data_edit.html")

# # Alle Benutzer abrufen
# @app.route("/api/users", methods=["GET"])
# def get_users():
#     pass

# # Benutzer hinzufügen
# @app.route("/api/users", methods=["POST"])
# def add_user():
#     pass

if __name__ == "__main__":
    # use_reloader=False ist der Schlüssel für VS Code Debugging!
    app.run(host="127.0.0.1", port=3000, debug=True, use_reloader=False)
