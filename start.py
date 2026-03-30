# run_app.py (im Hauptordner speichern)
import subprocess
import sys

if __name__ == "__main__":
    print("Starte Finanzapp via uv...")
    subprocess.run(["uv", "run", "python", "src/server.py"])