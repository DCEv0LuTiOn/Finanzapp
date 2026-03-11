from flask import Flask, render_template, request 

# Flask App definieren, static_folder auf public setzen
app = Flask(__name__, static_folder="public", static_url_path="")

# Startseite ausliefern
@app.route("/")
def index():
    return render_template("index.html")

# Alle Benutzer abrufen
@app.route("/api/users", methods=["GET"])
def get_users():
    pass

# Benutzer hinzufügen
@app.route("/api/users", methods=["POST"])
def add_user():
    pass

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000, debug=True)
