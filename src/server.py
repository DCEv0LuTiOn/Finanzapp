from flask import Flask, render_template, request, redirect,url_for, session
from functools import wraps  # sorgt dafür, dass die Route ihren echten Namen behält für decorator benötigt
import db
from dtos import *
import hashlib
import calendar
from datetime import datetime, timedelta

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
        user:KontoinhaberDTO = db.get_user_by_email(email)
        if user:
            if user.Email == email and user.Passwort == hash_password(password):
                session["user_id"] = user.ID  # Session sicher machen userid in session speichern
                session["name"] = user.Vorname + " " + user.Nachname
                return redirect(url_for("menue"))
            else:
                error = "E-Mail oder Passwort falsch"
        else:
            error = "E-Mail oder Passwort falsch"

    return render_template("login.html", error=error)

# Startseite ausliefern
@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/sign_up", methods=["POST"])
def sign_up():

    kontoinhaber = KontoinhaberDTO(
        Vorname= request.form["txt_vorname"],
        Nachname= request.form["txt_nachname"],
        Email= request.form["txt_email"],
        Passwort= request.form["txt_password"]
    )

    best_password = request.form["txt_best_password"]
    
    if kontoinhaber.Passwort != best_password:
        error = "Passwörter stimmen nicht überein!"
        return render_template("registration.html", lblInfo=error)
    if db.get_user_by_email(kontoinhaber.Email) is not None:
        error = "E-Mail ist bereits registriert!"
        return render_template("registration.html", lblInfo=error)
    if not ("@" in kontoinhaber.Email and "." in kontoinhaber.Email):
        error = "E-Mail muss ein @ und einen Punkt enthalten!"
        return render_template("registration.html", lblInfo=error)    
    if len(kontoinhaber.Passwort) < 6:
        error = "Passwort muss mindestens 6 Zeichen lang sein!"
        return render_template("registration.html", lblInfo=error)
    if len(kontoinhaber.Vorname) == 0 or len(kontoinhaber.Nachname) == 0:
        error = "Vorname und Nachname dürfen nicht leer sein!"
        return render_template("registration.html", lblInfo=error)
    
    kontoinhaber.Passwort = hash_password(kontoinhaber.Passwort)

    db.execute_insert_dtos(kontoinhaber)
    return redirect(url_for("login"))
    

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/menue", methods=["GET", "POST"])
@login_required
def menue():
    kategorien:list[KategorieDTO] = db.get_kategorien_by_kontoinhaber_id(session.get("user_id"))
    konten:list[KontoDTO] = db.get_konto_by_user_id(session.get("user_id"))
    
    # Default Datumsbereich
    start_date = ""
    end_date = ""
    
    # User hat Filter angewendet → in Session speichern
    if request.method == "POST":
        selected_kategorien = request.form.getlist("kategorie")
        session["selected_kategorien"] = selected_kategorien

        # Welcher Button wurde gedrückt?
        filter_btn = request.form.get("filter_btn")
        
        # Datumsbereich bestimmen mit der separaten Funktion
        start_date, end_date = filterdatum_auslesen(filter_btn)
        session["start_date"] = start_date
        session["end_date"] = end_date

        selected_konten = request.form.getlist("konto")
        session["selected_konten"] = selected_konten

        session.modified = True  # wichtig: Session-Änderung mitteilen
    else:
        if "start_date" in session and "end_date" in session:
            start_date = session["start_date"]
            end_date = session["end_date"]
        # Aus Session auslesen, oder alle Kategorien auswählen (Default)
        if "selected_kategorien" in session:
            selected_kategorien = session["selected_kategorien"]
        else:
            # Beim ersten Laden: alle Kategorie-IDs auswählen
            selected_kategorien = [str(kategorie.ID) for kategorie in kategorien]
            selected_kategorien.append("null")  # "Keine Kategorie" immer mit in die Filterung aufnehmen
        
        # Aus Session auslesen, oder alle Konten auswählen (Default)
        if "selected_konten" in session:
            selected_konten = session["selected_konten"]
        else:
            selected_konten = [str(konto.IBAN) for konto in konten]

    transaktionen = db.get_transaktionen_by_IBANs_and_Kategorie_IDs_and_date(selected_konten, selected_kategorien, start_date, end_date)
    print(len(transaktionen))
    
    return render_template("menue/menue.html",
                          user_name=session.get("name"),
                          kategorien=kategorien,
                          selected_kategorien=selected_kategorien,
                          start_date=start_date,
                          end_date=end_date,
                          konten=konten,
                          selected_konten=selected_konten)

#Menue ausliefern
@app.route("/data_input")
@login_required
def data_input():
    return render_template("data_input.html", user_name=session.get("name"))

#Menue ausliefern
@app.route("/data_edit")
@login_required
def data_edit():
    return render_template("data_edit.html", user_name=session.get("name"))

def filterdatum_auslesen(filter_btn):
    today = datetime.now().date()
    start_date = ""
    end_date = ""
    
    if filter_btn == "this_Month":
        # Dieses Monat: 1. bis Ende des Monats
        monthday, last_day = calendar.monthrange(today.year, today.month)
        end_date = datetime(today.year, today.month, last_day).strftime("%Y-%m-%d")
        start_date = datetime(today.year, today.month, 1).strftime("%Y-%m-%d")
    elif filter_btn == "last_30_days":
        # Letzte 30 Tage: heute minus 30 Tage bis heute
        end_date = today.strftime("%Y-%m-%d")
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    elif filter_btn == "current_quarter":
        # Aktuelles Quartal
        quarter = (today.month - 1) // 3  # 0=Q1, 1=Q2, 2=Q3, 3=Q4
        quarter_start_month = quarter * 3 + 1
        quarter_end_month = quarter * 3 + 3
        
        start_date = datetime(today.year, quarter_start_month, 1).strftime("%Y-%m-%d")
        if quarter_end_month == 3:
            end_date = datetime(today.year, 3, 31).strftime("%Y-%m-%d")
        elif quarter_end_month == 6:
            end_date = datetime(today.year, 6, 30).strftime("%Y-%m-%d")
        elif quarter_end_month == 9:
            end_date = datetime(today.year, 9, 30).strftime("%Y-%m-%d")
        else:  # quarter_end_month == 12
            end_date = datetime(today.year, 12, 31).strftime("%Y-%m-%d")
    elif filter_btn == "this_year":
        # Dieses Jahr: 1. Januar bis 31. Dezember
        end_date = datetime(today.year, 12, 31).strftime("%Y-%m-%d")
        start_date = datetime(today.year, 1, 1).strftime("%Y-%m-%d")
    elif filter_btn == "last_year":
        # Letztes Jahr: 1. Januar bis 31. Dezember
        end_date = datetime(today.year - 1, 12, 31).strftime("%Y-%m-%d")
        start_date = datetime(today.year - 1, 1, 1).strftime("%Y-%m-%d")
    elif filter_btn == "all":
        # Keine Datumsfilter
        start_date = ""
        end_date = ""
    elif filter_btn == "filter_apply":
        # "Filter anwenden" Button: benutzerdefinierter Datumsbereich
        # Der Aufrufer muss start_date und end_date aus request.form übergeben
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")
    else:
        # Fallback: keine Datumsfilter
        start_date = ""
        end_date = ""
    
    return (start_date, end_date)


if __name__ == "__main__":
    # use_reloader=False ist der Schlüssel für VS Code Debugging!
    app.run(host="127.0.0.1", port=3000, debug=True, use_reloader=False)
