import os
import sys
from src.server import app  # dein Flask app importieren

# in src wechseln
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

sys.path.insert(0, SRC_DIR)
os.chdir(SRC_DIR)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000, debug=True)