from flask import Flask, flash, render_template, request, redirect,url_for, session
from functools import wraps  # sorgt dafür, dass die Route ihren echten Namen behält für decorator benötigt
import db
from dtos import *
import hashlib
import calendar
from datetime import datetime, timedelta
import csv
import re


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
    filter_daten = get_filter_daten()
    kategorien = filter_daten["kategorien"]
    selected_kategorien = filter_daten["selected_kategorien"]
    start_date = filter_daten["start_date"]
    end_date = filter_daten["end_date"]
    konten = filter_daten["konten"]
    selected_konten = filter_daten["selected_konten"]
    
    transaktionen = db.get_transaktionen_by_IBANs_and_Kategorie_IDs_and_date(selected_konten, selected_kategorien, start_date, end_date)
    print(len(transaktionen))
    ausgaben_summe = sum([transaktion.Betrag for transaktion in transaktionen if transaktion.Betrag < 0])
    einnahmen_summe = sum([transaktion.Betrag for transaktion in transaktionen if transaktion.Betrag > 0])
    kontostand = sum([konto.Saldo for konto in konten if konto.IBAN in selected_konten])
    kategorie_dict = {}
    for kategorie in kategorien:
        if str(kategorie.ID) in selected_kategorien:
            kategorie_dict[kategorie.Bezeichnung] = {"ausgaben": 0, "einnahmen": 0}
            for transaktion in transaktionen:
                if transaktion.Kategorie_ID == kategorie.ID:
                    if transaktion.Betrag < 0:
                        kategorie_dict[kategorie.Bezeichnung]["ausgaben"] += transaktion.Betrag
                    else:
                        kategorie_dict[kategorie.Bezeichnung]["einnahmen"] += transaktion.Betrag
    
    # "Keine Kategorie" mit in die Auswertung aufnehmen (Transaktionen ohne Kategorie_ID)
    if "null" in selected_kategorien:
            kategorie_dict["Keine Kategorie"] = {"ausgaben": 0, "einnahmen": 0}
            for transaktion in transaktionen:
                if transaktion.Kategorie_ID == None:
                    if transaktion.Betrag < 0:
                        kategorie_dict["Keine Kategorie"]["ausgaben"] += transaktion.Betrag
                    else:
                        kategorie_dict["Keine Kategorie"]["einnahmen"] += transaktion.Betrag


    return render_template("menue/menue.html",
                            action="menue", # filter
                            user_name=session.get("name"), # navigation
                            kategorien=kategorien, # filter
                            selected_kategorien=selected_kategorien, # filter
                            start_date=start_date, # filter
                            end_date=end_date, # filter
                            konten=konten, # filter
                            selected_konten=selected_konten, # filter
                            ausgaben_summe=ausgaben_summe, # stats
                            einnahmen_summe=einnahmen_summe, # stats
                            kontostand=kontostand, # stats
                            kategorie_dict=kategorie_dict) # charts

#Menue ausliefern
@app.route("/data_input")
@login_required
def data_input():
    return render_template("data_input.html", 
                           user_name=session.get("name"), 
                           buchungsarten=db.get_all_buchungsarten(),
                           kategorien=db.get_kategorien_by_kontoinhaber_id(session.get("user_id")), 
                           waehrungen=db.get_all_waehrungen(), 
                           konten=db.get_all_konten_by_kontoinhaber_id(session.get("user_id")))

#Menue ausliefern
@app.route("/data_edit", methods=["GET", "POST"])
@login_required
def data_edit():
    filter_daten = get_filter_daten()
    kategorien = filter_daten["kategorien"]
    selected_kategorien = filter_daten["selected_kategorien"]
    konten = filter_daten["konten"]
    selected_konten = filter_daten["selected_konten"]
    buchungsarten = db.get_all_buchungsarten()
    data = []
    if "filter_data" in session:
        filter_data = session["filter_data"]
    else:
        filter_data = TransaktionDTO(
            ID="", 
            IBAN_Auftragskonto="", 
            IBAN_Zahlungsbeteiligter="", 
            Name_Zahlungsbeteiligter="", 
            Verwendungszweck="", 
            Betrag=0.00, 
            Saldo_nach_Buchung=0.00,
            Buchungsart_ID="", 
            Bemerkung=""
        )

    if  request.form.get("btn_filter_transaktion") == "filter":

        if request.form.get("txt_transaktionsdatum_von_filter"):
            datum_von = datetime.strptime(request.form.get("txt_transaktionsdatum_von_filter"), "%Y-%m-%d")
            datum_von = str(datum_von.strftime( "%Y-%m-%d")) #"%d.%m.%Y"
        if request.form.get("txt_transaktionsdatum_bis_filter"):
            datum_bis = datetime.strptime(request.form.get("txt_transaktionsdatum_bis_filter"), "%Y-%m-%d")
            datum_bis = str(datum_bis.strftime( "%Y-%m-%d")) #"%d.%m.%Y"

        filter_data = TransaktionDTO(   
                ID=request.form.get("txt_id_filter"),
                IBAN_Zahlungsbeteiligter=request.form.get("txt_iban_zahlungsbeteiligter_filter"),
                Name_Zahlungsbeteiligter=request.form.get("txt_name_zahlungsbeteiligter_filter"),
                Verwendungszweck=request.form.get("txt_verwendungszweck_filter"),
                Betrag=float(request.form.get("txt_betrag_filter").replace(",", ".") if request.form.get("txt_betrag_filter") else 0.00),
                Saldo_nach_Buchung=float(request.form.get("txt_saldo_nach_buchung_filter").replace(",", ".") if request.form.get("txt_saldo_nach_buchung_filter") else 0.00),
                Transaktions_Datum= datum_von if request.form.get("txt_transaktionsdatum_von_filter") else None,

                Buchungsart_ID=db.get_id_by_buchungsart(request.form.get("txt_buchungsart_filter")).ID if request.form.get("txt_buchungsart_filter") else None,
                Bemerkung=request.form.get("txt_bemerkung_filter")
        )
        session["filter_data"] = filter_data
        
        data = db.get_filtered_transaktionen(filter_data, session.get("user_id"), datum_bis if request.form.get("txt_transaktionsdatum_bis_filter") else None, selected_konten, selected_kategorien)
    
    return render_template("data_edit/data_edit.html",
                            user_name=session.get("name"),
                            kategorien=kategorien,
                            selected_kategorien=selected_kategorien,
                            konten=konten,
                            selected_konten=selected_konten,
                            buchungsarten=buchungsarten,
                            filter_data=filter_data,
                            Transaktions_Datum_Bis=datum_bis if request.form.get("txt_transaktionsdatum_bis_filter") else None,
                            data=data)

# data_edit
@app.route("/update_konto", methods=["POST"])
@login_required
def update_konto():
    iban = request.form.get("iban")
    neuer_name = request.form.get("neuer_name")

    if iban and neuer_name:
        konto:KontoDTO = db.get_konto_by_iban(iban)
        konto.Konto_Name = neuer_name
        db.execute_update_dtos(konto)    
    return redirect(url_for("data_edit"))

# data_edit
@app.route("/delete_konto_form/<iban>", methods=["POST"])
@login_required
def delete_konto(iban):
    konto:KontoDTO = db.get_konto_by_iban(iban)
    transaktionen:list[TransaktionDTO] = db.get_Transaktionen_by_konto_iban(iban)
    db.execute_delete_dtos(transaktionen)
    db.execute_delete_dtos(konto)
    return redirect(url_for("data_edit"))

# data_edit
@app.route("/update_kategorie", methods=["POST"])
@login_required
def update_kategorie():
    kat_id = request.form.get("id")
    bezeichnung = request.form.get("bezeichnung")
    user_id = session.get("user_id")
    
    if kat_id and bezeichnung:
        kategorie:KategorieDTO = KategorieDTO(kat_id, bezeichnung, user_id)
        db.execute_update_dtos(kategorie)
        
    return redirect(url_for("data_edit"))

# data_edit
@app.route("/delete_kategorie/<int:kat_id>", methods=["POST"])
@login_required
def delete_kategorie(kat_id):
    kategorie:KategorieDTO = db.get_kategorie_by_id(kat_id)
    transaktionen:list[TransaktionDTO] = db.get_Transaktionen_by_kategorie_id(kat_id)
    for transaktion in transaktionen:
        transaktion.Kategorie_ID = None  # Kategorie entfernen, Transaktion aber behalten
    db.execute_update_dtos(transaktionen)  # Alle betroffenen Transaktionen aktualisieren
    db.execute_delete_dtos(kategorie)
    return redirect(url_for("data_edit"))

@app.route("/delete_transaction/<int:trans_id>", methods=["POST"])
@login_required
def delete_transaction(trans_id):
    transaktion:TransaktionDTO = db.get_transaktion_by_id(trans_id)
    db.execute_delete_dtos(transaktion)
    return redirect(url_for("data_edit"))

#Menue ausliefern
@app.route("/update_transaktion", methods=["POST"])  # GET ist hier meist nicht nötig
@login_required
def update_transaktion():
    if request.method == "POST":
        try:
            transaktion = db.get_transaktion_by_id(request.form.get("id"))

            # 1. Daten aus dem Formular abgreifen (Namen aus dem Popup-HTML)
            transaktion.IBAN_Zahlungsbeteiligter = request.form.get("iban_beteiligter")
            transaktion.Name_Zahlungsbeteiligter = request.form.get("name_beteiligter")
            transaktion.Verwendungszweck = request.form.get("verwendungszweck")

            # Betrag sicher umwandeln
            betrag_raw = request.form.get("betrag")
            transaktion.Betrag = float(betrag_raw.replace(",", ".")) if betrag_raw else 0.0
            
            transaktion.Transaktions_Datum = request.form.get("datum")
            transaktion.Bemerkung = request.form.get("bemerkung")
            
            # IDs abgreifen
            transaktion.Buchungsart_ID = request.form.get("buchungsart_id")
            transaktion.Kategorie_ID = request.form.get("kategorie_id")

            # 2. Spezialfall: "Keine Kategorie" (null) behandeln
            if transaktion.Kategorie_ID == "null":
                transaktion.Kategorie_ID = None
            else:
                transaktion.Kategorie_ID = int(transaktion.Kategorie_ID)

            # Buchungsart_ID ist ein Pflichtfeld, aber sicherheitshalber trotzdem umwandeln
            transaktion.Buchungsart_ID = int(transaktion.Buchungsart_ID) if transaktion.Buchungsart_ID else None
            

            # 4. Datenbank-Aufruf zum Aktualisieren der Transaktion
            db.execute_update_dtos(transaktion)
            
            # Erfolg melden
            flash("Eintrag erfolgreich aktualisiert", "success")

        except Exception as e:
            print(f"Fehler beim Update: {e}")
            # flash(f"Fehler beim Speichern: {e}", "danger")

    return redirect(url_for("data_edit"))

def get_filter_daten() -> list[TransaktionDTO]:
    kategorien:list[KategorieDTO] = db.get_kategorien_by_kontoinhaber_id(session.get("user_id"))
    konten:list[KontoDTO] = db.get_all_konten_by_kontoinhaber_id(session.get("user_id"))
    
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

    return {"kategorien": kategorien,
            "selected_kategorien": selected_kategorien,
            "start_date": start_date,
            "end_date": end_date,
            "konten": konten,
            "selected_konten": selected_konten}

def filterdatum_auslesen(filter_btn):
    #Fiterfunktion für das Menü
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


#Dateininput 
@app.route("/data_input", methods=["POST"])
@login_required
def data_input_post():

    if  request.form.get("btn_transaktion_insert") == "transaktion":  
        return input_transaction()

    #Konto Insert Button                                                               
    if  request.form.get("btn_konto_insert") == "konto": 
        return input_konto()

    #welcher Button wurde gedrückt? -> über name des Buttons im HTML-Formular
    #Upload Button
    if  request.form.get("btn_csv_upload") == "csv_upload":
    # "uploaded_file" ist der Name des Input-Felds im HTML-Formular
        uploaded_file = request.files.get("file_csv_Upload") 
        if uploaded_file:
            extract_data(uploaded_file)

            return render_template("data_input.html", 
                                   user_name=session.get("name"), 
                                   kategorien=db.get_kategorien_by_kontoinhaber_id(session.get("user_id")), 
                                   buchungsarten=db.get_all_buchungsarten(), 
                                   waehrungen=db.get_all_waehrungen(),
                                   konten=db.get_all_konten_by_kontoinhaber_id(session.get("user_id")), 
                                   transaction_correct="CSV-Datei erfolgreich hochgeladen und Daten in die Datenbank eingefügt!")  
 
    
    #welcher Button wurde gedrückt? -> über name des Buttons im HTML-Formular
    #kategorien Button
    if  request.form.get("btn_kategorien_insert") == "kategorien":    
        return input_kategorie()

    #welcher Button wurde gedrückt? -> über name des Buttons im HTML-Formular
    #bank Button
    if  request.form.get("btn_bank_insert") == "bank":    
        return input_bank()

    return redirect(url_for("data_input"))



def input_transaction():
        #Plausibilitätsprüfungen für die Transaktionsdaten
        #Auftragskonto darf nicht leer sein
        error = None

        print( betrag_valid(str.strip(request.form.get("txt_betrag_insert").replace(",", "."))))

        if str.strip(request.form.get("ddm_iban_auftragskonto_insert")) == "":
            error = "IBAN Auftragskonto darf nicht leer sein!"

            
        #IBAN Zahlungsbeteiligter 
        #Zahlungsbeiteligter darf leer sein, wenn es sich um eine Barauszahlung handelt, ansonsten muss er ausgefüllt werden
        elif str.strip(request.form.get("txt_iban_zahlungsbeteiligter_insert").upper()) == "" and str.strip(request.form.get("ddm_buchungsart_insert")) != "8":
            error = "IBAN Zahlungsbeteiligter darf nicht leer sein!"
        elif got_special_characters(str.strip(request.form.get("txt_iban_zahlungsbeteiligter_insert").upper())) and str.strip(request.form.get("ddm_buchungsart_insert")) != "8":
            error = "IBAN Zahlungsbeteiligter enthält Sonderzeichen!"
        elif iban_valid(str.strip(request.form.get("txt_iban_zahlungsbeteiligter_insert").upper())) == False and str.strip(request.form.get("ddm_buchungsart_insert")) != "8":
            error = "IBAN Zahlungsbeteiligter ist ungültig!"

        #Name Zahlungsbeteiligter
        elif str.strip(request.form.get("txt_name_zahlungsbeteiligter_insert")) == "" and str.strip(request.form.get("ddm_buchungsart_insert")) != "8":
            error = "Name Zahlungsbeteiligter darf nicht leer sein!"

        #Verwendungszweck
        elif str.strip(request.form.get("txt_verwendungszweck_insert")) == "":
            error = "Verwendungszweck darf nicht leer sein!"

        #Betrag
        elif str.strip(request.form.get("txt_betrag_insert")) == "":
            error = "Betrag darf nicht leer sein!"
        elif betrag_valid(str.strip(request.form.get("txt_betrag_insert").replace(",", "."))) == None:
            error = "Betrag ist ungültig! Bitte nur Zahlen eingeben, Dezimaltrennzeichen ist ein Komma!"

        #Saldo nach Buchung
        # elif str.strip(request.form.get("txt_saldo_nach_buchung_insert")) == "":
        #     error = "Saldo nach Buchung darf nicht leer sein!"
        # elif betrag_valid(str.strip(request.form.get("txt_saldo_nach_buchung_insert"))) == False:
        #     error = "Saldo nach Buchung ist ungültig! Bitte nur Zahlen eingeben, Dezimaltrennzeichen ist ein Komma!"

        #Transaktionsdatum
        elif str.strip(request.form.get("txt_transaktionsdatum_insert")) == "":
            error = "Transaktionsdatum darf nicht leer sein!"
            
        elif str.strip(request.form.get("ddm_buchungsart_insert")) == "":
            error = "Buchungsart muss ausgewählt werden!"
        elif str.strip(request.form.get("ddm_kategorie_insert")) == "":
            error = "Kategorie muss ausgewählt werden!"

        #prüft ob ein Fehler aus den Plausibilitätsprüfungen vorliegt, wenn ja wird die Seite mit Fehlermeldung neu geladen   
        if error is not None:
            return render_template("data_input.html", 
                                   user_name=session.get("name"), 
                                   buchungsarten=db.get_all_buchungsarten(),
                                   kategorien=db.get_kategorien_by_kontoinhaber_id(session.get("user_id")), 
                                   waehrungen=db.get_all_waehrungen(), 
                                   konten=db.get_all_konten_by_kontoinhaber_id(session.get("user_id")), 
                                   transaction_error=error)    
        
        datum = datetime.strptime(request.form.get("txt_transaktionsdatum_insert"), "%Y-%m-%d")
        datum = str(datum.strftime("%Y-%m-%d"))

        transaction = TransaktionDTO(
                IBAN_Auftragskonto=request.form.get("ddm_iban_auftragskonto_insert"),
                IBAN_Zahlungsbeteiligter=request.form.get("txt_iban_zahlungsbeteiligter_insert").upper(),
                Name_Zahlungsbeteiligter=request.form.get("txt_name_zahlungsbeteiligter_insert"),
                Verwendungszweck=request.form.get("txt_verwendungszweck_insert"),
                Betrag=float(request.form.get("txt_betrag_insert").replace(",", ".")),
                Transaktions_Datum=datum,
                Buchungsart_ID=request.form.get("ddm_buchungsart_insert"),
                Kategorie_ID=request.form.get("ddm_kategorie_insert"),
                Bemerkung=request.form.get("txt_bemerkung_insert")
            )
        
        # Berechnet den neuen Saldo des Kontos nach der Buchung und aktualisiert diesen in der Datenbank
        konto:KontoDTO = db.get_konto_by_iban(transaction.IBAN_Auftragskonto)
        konto.Saldo += transaction.Betrag
        transaction.Saldo_nach_Buchung = konto.Saldo

        db.execute_insert_dtos(transaction)
        db.execute_update_dtos(konto)
        return render_template("data_input.html", user_name=session.get("name"), 
                               buchungsarten=db.get_all_buchungsarten(),
                               kategorien=db.get_kategorien_by_kontoinhaber_id(session.get("user_id")), 
                               waehrungen=db.get_all_waehrungen(), 
                               konten=db.get_all_konten_by_kontoinhaber_id(session.get("user_id")), 
                               transaction_correct="Transaktion erfolgreich hinzugefügt!")    
    

def input_konto():
        error = None
        
        #Plausibilitätsprüfungen für die Kontodaten
        #IBAN  
        if str.strip(request.form.get("txt_iban_konto_insert")) == "":
            error = "IBAN darf nicht leer sein!"
        elif got_special_characters(str.strip(request.form.get("txt_iban_konto_insert").upper())):
            error = "IBAN enthält Sonderzeichen!"
        elif iban_valid(str.strip(request.form.get("txt_iban_konto_insert").upper())) == False:
            error = "IBAN ist ungültig!"
        elif db.get_konto_by_iban(str.strip(request.form.get("txt_iban_konto_insert").upper())) is not None:
            error = "IBAN ist bereits vorhanden!"
        elif db.get_bank_by_blz(str.strip(request.form.get("txt_iban_konto_insert").upper()[4:12])) is None:
            error = "Die BLZ aus der IBAN ist nicht in der Datenbank vorhanden! Bitte zuerst die Bank mit der entsprechenden BLZ anlegen!"


        #BIC
        elif str.strip(request.form.get("txt_bic_konto_insert")) == "":
            error = "BIC darf nicht leer sein!"
        elif got_special_characters(str.strip(request.form.get("txt_bic_konto_insert"))):
            error = "BIC enthält Sonderzeichen!"
        elif bic_valid(str.strip(request.form.get("txt_bic_konto_insert"))) == False:
            error = "BIC ist ungültig!"
        
        #Konto Name
        elif str.strip(request.form.get("txt_konto_name_insert")) == "":
            error = "Konto Name darf nicht leer sein!"

        #Saldo
        elif str.strip(request.form.get("txt_saldo_konto_insert")) == "":
            error = "Saldo darf nicht leer sein!"
        elif betrag_valid(str.strip(request.form.get("txt_saldo_konto_insert"))) == False:
            error = "Saldo ist ungültig! Bitte nur Zahlen eingeben, Dezimaltrennzeichen ist ein Komma!"
        
        #Währung
        elif str.strip(request.form.get("ddm_waehrung_konto_insert"))  == "":
            error = "Währung muss ausgewählt werden!"   

        #error anzeigen wenn eine der Plausibilitätsprüfungen fehlschlägt, ansonsten Konto in die Datenbank einfügen
        if error is not None:
            return render_template("data_input.html", 
                                   user_name=session.get("name"), 
                                   buchungsarten=db.get_all_buchungsarten(),
                                   kategorien=db.get_kategorien_by_kontoinhaber_id(session.get("user_id")), 
                                   waehrungen=db.get_all_waehrungen(), 
                                   konten=db.get_all_konten_by_kontoinhaber_id(session.get("user_id")), 
                                   konto_error=error)    
        
        konto = KontoDTO(
            IBAN=request.form.get("txt_iban_konto_insert"),
            BIC=request.form.get("txt_bic_konto_insert"),
            BLZ=request.form.get("txt_iban_konto_insert")[4:12],
            Konto_Name=request.form.get("txt_konto_name_insert"),
            Kontoinhaber_ID=session.get("user_id"),
            Saldo=request.form.get("txt_saldo_konto_insert").replace(",", "."),
            Waehrung_ID=request.form.get("ddm_waehrung_konto_insert")
        )

        db.execute_insert_dtos(konto)
        return render_template("data_input.html", 
                                user_name=session.get("name"),
                                buchungsarten=db.get_all_buchungsarten(),
                                kategorien=db.get_kategorien_by_kontoinhaber_id(session.get("user_id")), 
                                waehrungen=db.get_all_waehrungen(), 
                                konten=db.get_all_konten_by_kontoinhaber_id(session.get("user_id")), 
                                konto_correct="Konto erfolgreich hinzugefügt!")    
    

def input_kategorie():
    #Funktion fügt eine neue Kategorie mit ein
    error = None

    #Plausibilitätsprüfungen
    #Kategorie Name
    if str.strip(request.form.get("txt_kategorie_name_insert")) == "":
        error = "Kategorie darf nicht leer sein!"
    elif got_special_characters(str.strip(request.form.get("txt_kategorie_name_insert"))):
        error = "Kategorie enthält Sonderzeichen!"
    elif db.get_id_by_kategorie(str.strip(request.form.get("txt_kategorie_name_insert")), session.get("user_id")) is not None:
        error = "Kategorie ist bereits vorhanden!"
    #error anzeigen wenn eine der Plausibilitätsprüfungen fehlschlägt, ansonsten Kategorie in die Datenbank einfügen
    if error is not None:  
        return render_template("data_input.html", 
                               user_name=session.get("name"), 
                               buchungsarten=db.get_all_buchungsarten(),
                               kategorien=db.get_kategorien_by_kontoinhaber_id(session.get("user_id")), 
                               waehrungen=db.get_all_waehrungen(), 
                               konten=db.get_all_konten_by_kontoinhaber_id(session.get("user_id")), 
                               kategorie_error=error)
    
    kategorie = KategorieDTO(
        Bezeichnung=request.form.get("txt_kategorie_name_insert"),
        Kontoinhaber_ID=session.get("user_id")
    )
    db.execute_insert_dtos(kategorie)
    return render_template("data_input.html", 
                           user_name=session.get("name"), 
                           buchungsarten=db.get_all_buchungsarten(),
                           kategorien=db.get_kategorien_by_kontoinhaber_id(session.get("user_id")), 
                           waehrungen=db.get_all_waehrungen(), 
                           konten=db.get_all_konten_by_kontoinhaber_id(session.get("user_id")), 
                           kategorie_correct="Kategorie erfolgreich hinzugefügt!")
    

def input_bank():
        #Funktion fügt eine neue Bank ein 
        error = None
        #Plausibilitätsprüfungen
        #BLZ
        if str.strip(request.form.get("txt_blz_bank_insert")) == "":
            error = "BLZ darf nicht leer sein!" 
        elif got_special_characters(str.strip(request.form.get("txt_blz_bank_insert"))):
            error = "BLZ enthält Sonderzeichen!"
        elif db.get_bank_by_blz(str.strip(request.form.get("txt_blz_bank_insert"))) is not None:
            error = "BLZ ist bereits vorhanden!"
        elif blz_valid(str.strip(request.form.get("txt_blz_bank_insert"))) == False:
            error = "BLZ ist ungültig! Bitte prüfen Sie ihre Eingabe!"
        
        #Bank Name
        elif str.strip(request.form.get("txt_name_bank_insert")) == "":
            error = "Bank Name darf nicht leer sein!"

        #error anzeigen wenn eine der Plausibilitätsprüfungen fehlschlägt, ansonsten Bank in die Datenbank einfügen
        if error is not None:  
            return render_template("data_input.html", 
                                   user_name=session.get("name"), 
                                   buchungsarten=db.get_all_buchungsarten(),
                                   kategorien=db.get_kategorien_by_kontoinhaber_id(session.get("user_id")), 
                                   waehrungen=db.get_all_waehrungen(), 
                                   konten=db.get_all_konten_by_kontoinhaber_id(session.get("user_id")), 
                                   bank_error=error)

        bank = BankDTO(
            BLZ=request.form.get("txt_blz_bank_insert"),
            Name=request.form.get("txt_name_bank_insert")
        )
        db.execute_insert_dtos(bank)
        return render_template("data_input.html", 
                               user_name=session.get("name"), 
                               buchungsarten=db.get_all_buchungsarten(),
                               kategorien=db.get_kategorien_by_kontoinhaber_id(session.get("user_id")), 
                               waehrungen=db.get_all_waehrungen(), 
                               konten=db.get_all_konten_by_kontoinhaber_id(session.get("user_id")), 
                               bank_correct="Bank erfolgreich hinzugefügt!")


def extract_data(file) -> list[TransaktionDTO]:
    
    list_data = []
    if file:

        stream = file.stream.read().decode("utf-8").splitlines()
        reader = csv.DictReader(stream, delimiter=';')

        first_row = next(reader, None)

        new_bank = BankDTO(
            BLZ=first_row["IBAN Auftragskonto"][4:12],
            Name=first_row["Bankname Auftragskonto"]
        )

        #Prüft ob die jeweilige Bank bereits in der Datenbank vorhanden ist, wenn nicht wird sie eingefügt
        if db.get_bank_by_blz(new_bank.BLZ) is None:
            db.execute_insert_dtos(new_bank)

        #Prüft ob die jeweilige Währung bereits in der Datenbank vorhanden ist, wenn nicht wird sie eingefügt
        waehrung = WaehrungDTO(Waehrung=first_row["Waehrung"])
        if db.get_id_by_waehrung(first_row.get("Waehrung")) is None:
            db.execute_insert_dtos(waehrung)

        new_konto = KontoDTO(
            IBAN=first_row["IBAN Auftragskonto"],
            BIC=first_row["BIC Auftragskonto"],
            BLZ=first_row["IBAN Auftragskonto"][4:12],
            Konto_Name=db.get_user_by_id(session.get("user_id")).Vorname + " " + db.get_user_by_id(session.get("user_id")).Nachname + " Konto",
            Kontoinhaber_ID=session.get("user_id"),
            Saldo=0.00,
            Waehrung_ID=db.get_id_by_waehrung(first_row.get("Waehrung")).ID
        )

        #Prüft ob das jeweilige Konto bereits in der Datenbank vorhanden ist, wenn nicht wird es eingefügt
        if db.get_konto_by_iban(new_konto.IBAN) is None:
            db.execute_insert_dtos(new_konto)   

        #Prüft ob die jeweilige Buchungsart bereits in der Datenbank vorhanden ist, wenn nicht wird sie eingefügt
        new_buchungsart = BuchungsartDTO(Buchungsart=first_row.get("Buchungstext"))
        if db.get_id_by_buchungsart(new_buchungsart.Buchungsart) is None: 
                db.execute_insert_dtos(new_buchungsart)


        datum = datetime.strptime(first_row.get("Valutadatum"), "%d.%m.%Y")
        datum = str(datum.strftime("%Y-%m-%d"))

        transaction = TransaktionDTO(   
                IBAN_Auftragskonto=first_row.get("IBAN Auftragskonto"),
                IBAN_Zahlungsbeteiligter=first_row.get("IBAN Zahlungsbeteiligter"),
                Name_Zahlungsbeteiligter=first_row.get("Name Zahlungsbeteiligter"),
                Verwendungszweck=first_row.get("Verwendungszweck"),
                Betrag=float(first_row.get("Betrag").replace(",", ".")),
                Transaktions_Datum=datum,
                # Kategorie_ID=1,
                Buchungsart_ID=db.get_id_by_buchungsart(first_row.get("Buchungstext")).ID,
                Bemerkung=""
            )
        
        konto:KontoDTO = db.get_konto_by_iban(transaction.IBAN_Auftragskonto)
        konto.Saldo += transaction.Betrag
        transaction.Saldo_nach_Buchung = konto.Saldo
        db.execute_update_dtos(konto)
        # list_data.append(transaction)  
        # Man könnte es auch wie in der zeile darüber über die Liste appenden und am Ende ausführen     
        db.execute_insert_dtos(transaction)
        
        #geht zeile für zeile durch die csv datei durch und fügt die Daten in die Datenbank ein, dabei werden auch die Konten, Banken, Buchungsarten und Währungen angelegt, wenn sie noch nicht vorhanden sind
        for row in reader:
            
            new_buchungsart = BuchungsartDTO(Buchungsart=row.get("Buchungstext"))
            if db.get_id_by_buchungsart(new_buchungsart.Buchungsart) is None: 
                db.execute_insert_dtos(new_buchungsart)

            datum = datetime.strptime(row.get("Valutadatum"), "%d.%m.%Y")
            datum = str(datum.strftime("%Y-%m-%d"))

            transaction = TransaktionDTO(   
                IBAN_Auftragskonto=row.get("IBAN Auftragskonto"),
                IBAN_Zahlungsbeteiligter=row.get("IBAN Zahlungsbeteiligter"),
                Name_Zahlungsbeteiligter=row.get("Name Zahlungsbeteiligter"),
                Verwendungszweck=row.get("Verwendungszweck"),
                Betrag=float(row.get("Betrag").replace(",", ".")),
                Transaktions_Datum=datum,
                Buchungsart_ID=db.get_id_by_buchungsart(row.get("Buchungstext")).ID,
                Bemerkung=""
            )

            # Saldo nach Buchung berechnen: aktueller Saldo des Kontos + Betrag der Transaktion
            konto:KontoDTO = db.get_konto_by_iban(transaction.IBAN_Auftragskonto)
            konto.Saldo += transaction.Betrag
            transaction.Saldo_nach_Buchung = konto.Saldo
            db.execute_update_dtos(konto)
            list_data.append(transaction)

        db.execute_insert_dtos(list_data)


    return list_data

#prüfen ob Sonderzeichen in einem String vorhanden sind
def got_special_characters(text):
    return bool(re.search(r"[^a-zA-Z0-9]", text))

def iban_valid(iban):
    iban = iban.replace(" ", "").upper()

    # Grundstruktur
    if not re.match(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]+$", iban):
        return False

    # Länge prüfen (Beispiel DE)
    if len(iban) != 22:
        return False

    # Prüfziffer-Algorithmus
    rearranged = iban[4:] + iban[:4]

    # Buchstaben ersetzen
    numeric = ""
    for ch in rearranged:
        if ch.isdigit():
            numeric += ch
        else:
            numeric += str(ord(ch) - 55)  # A=10, B=11, ...

    # Modulo 97
    return int(numeric) % 97 == 1

#funktion prüft ob eine BIC gültig ist, d.h. ob sie dem Standardformat entspricht (4 Buchstaben für Bankcode, 2 Buchstaben für Ländercode, 2 alphanumerische Zeichen für Standortcode und optional 3 alphanumerische Zeichen für Filialcode) und keine Sonderzeichen enthält
def bic_valid(bic: str) -> bool:
    if not bic:
        return False

    bic = bic.strip().upper()

    muster = r"^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$"

    return bool(re.match(muster, bic))

#funktion prüft ob ein Betrag gültig ist, d.h. ob er nur Zahlen und maximal ein Dezimaltrennzeichen (Punkt oder Komma) enthält 
def betrag_valid(betrag: str) -> bool:
    #prüft ob ein Betrag richtig eingegeben wurde.
    if not betrag:
        return False

    betrag = betrag.strip()

    # Internationale Schreibweise: -1234.56 oder 1234.56
    muster_int = r"^-?[0-9]+(\.[0-9]{1,2})?$"

    return re.match(muster_int, betrag)


def blz_valid(blz: str) -> bool:
    #prüft ob eine BLZ gültig ist
    if not blz:
        return False

    blz = blz.strip()

    muster = r"^[0-9]{8}$"

    return bool(re.match(muster, blz))

if __name__ == "__main__":
    # use_reloader=False ist der Schlüssel für VS Code Debugging!
    app.run(host="127.0.0.1", port=3000, debug=True, use_reloader=False)
