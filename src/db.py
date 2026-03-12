import sqlite3
import sys
from contextlib import closing
from dtos import *


def execute_select_dto_list(sql:str,dto_class) -> list[object]: # sql und den Datentype bzw. die DTO Klasse
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;") # wird von sqlight3 benötigt das forgein_keys funktionieren
        connection.row_factory = sqlite3.Row            # wird von sqlight3 benötigt das man spaltennamen im cursor mit cursor.description rauslesen kann
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql)
            column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
            results = []
            for row in cursor.fetchall(): # alle daten vom select holen
                row_dict = dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben
                results.append(dto_class(**row_dict))  # alle zeilen vom dictionary der DTO Klasse hinzufügen
                                                    # anhand der spalten namen von select und DTO Variablen namen 
                                                    # => namen müssen gleich sein
            return results

def execute_select_dto(sql:str,dto_class) -> object: # sql und den Datentype bzw. die DTO Klasse
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;") 
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql)
            column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
            row =  cursor.fetchone() # daten vom select holen
            row_dict = dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben
            return dto_class(**row_dict)  # alle zeilen vom dictionary der DTO Klasse hinzufügen
                                                    # anhand der spalten namen von select und DTO Variablen namen 
                                                    # => namen müssen gleich sein

def execute_select_value(sql:str) -> str|int|float: # sql und den Datentype bzw. die DTO Klasse
    with sqlite3.connect(__db_path) as connection:  # Connection automatisch schließen
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql)
            row = cursor.fetchone() # daten vom select holen
            return row[0]
        
def execute_insert_dto_list(dtos:list[object]):
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        with closing(connection.cursor()) as cursor:
            try:
                for dto in dtos:
                    fields_to_insert = []
                    placeholders = []
                    values = {}
                    for key, value in dto.__dict__.items(): # variablen aus DTO holen
                        if key != "ID" and value is not None:
                            fields_to_insert.append(key)
                            placeholders.append(":" + key)
                            values[key] = value

                    table_name = dto.__class__.__name__[:dto.__class__.__name__.find("DTO")] # Holt sich aus der DTO den Namen der Klasse und schneidet DTO ab am ende
                    sql = f"INSERT INTO {table_name} ({', '.join(fields_to_insert)}) VALUES ({', '.join(placeholders)})"
                    cursor.execute(sql, values)
                connection.commit
            except sqlite3.DatabaseError as e:
                connection.rollback()
                print("DB Fehler:", e)
                raise

def execute_insert_dto(dto:object):
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        with closing(connection.cursor()) as cursor:
            try:
                fields_to_insert = []
                placeholders = []
                values = {}
                for key, value in dto.__dict__.items(): # variablen aus DTO holen
                    if key != "ID" and value is not None:
                        fields_to_insert.append(key)
                        placeholders.append(":" + key)
                        values[key] = value

                table_name = dto.__class__.__name__[:dto.__class__.__name__.find("DTO")] # Holt sich aus der DTO den Namen der Klasse und schneidet DTO ab am ende
                sql = f"INSERT INTO {table_name} ({', '.join(fields_to_insert)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(sql, values)
                connection.commit
            except sqlite3.DatabaseError as e:
                connection.rollback()
                print("DB Fehler:", e)
                raise

def execute_update_dto_list():
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        with closing(connection.cursor()) as cursor:
            try:
                pass
                # Noch zu tun
                connection.commit
            except sqlite3.DatabaseError as e:
                connection.rollback()
                print("DB Fehler:", e)
                raise
            
def execute_update_dto():
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        with closing(connection.cursor()) as cursor:
            try:
                pass
                # Noch zu tun
                connection.commit
            except sqlite3.DatabaseError as e:
                connection.rollback()
                print("DB Fehler:", e)
                raise

def get_users():
    sql = "SELECT * FROM kontoinhaber"
    users = execute_select_dto_list(sql,KontoinhaberDTO)
    user = execute_select_dto(sql,KontoinhaberDTO)
    # value_select = execute_select_value("SELECT id FROM user where id = '1'")
    execute_insert_dto(users[0])
    print(users)

def __create_Database():
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")

        connection.execute("""CREATE TABLE IF NOT EXISTS Kontoinhaber (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Vorname TEXT NOT NULL,
            Nachname TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE,
            Passwort TEXT NOT NULL
        )""")
        
        connection.execute("""CREATE TABLE IF NOT EXISTS Konto (
            IBAN TEXT PRIMARY KEY,
            BIC TEXT NOT NULL,
            Bank_Name TEXT NOT NULL,
            Konto_Name TEXT NOT NULL,
            Kontoinhaber_ID INTEGER NOT NULL,
            Saldo REAL NOT NULL DEFAULT 0,
            Waehrung TEXT NOT NULL,
            FOREIGN KEY (Kontoinhaber_ID) 
                REFERENCES Kontoinhaber(ID)
                ON DELETE CASCADE
        )""")
        
        connection.execute("""CREATE TABLE IF NOT EXISTS Buchungsart (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Buchungsart TEXT NOT NULL UNIQUE
        )""")
        
        connection.execute("""CREATE TABLE IF NOT EXISTS Kategorie (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Bezeichnung TEXT NOT NULL,
            Kontoinhaber_ID INTEGER NOT NULL,
            UNIQUE (Bezeichnung, Kontoinhaber_ID),
            FOREIGN KEY (Kontoinhaber_ID)
                REFERENCES Kontoinhaber(ID)
                ON DELETE CASCADE
        )""")
        
        connection.execute("""CREATE TABLE IF NOT EXISTS Transaktion (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            IBAN_Auftragskonto TEXT NOT NULL,
            IBAN_Zahlungsbeteiligter TEXT NOT NULL,
            Name_Zahlungsbeteiligter TEXT NOT NULL,
            Verwendungszweck TEXT,
            Betrag REAL NOT NULL,
            Saldo_nach_Buchung REAL NOT NULL,
            Transaktions_Datum TEXT NOT NULL,
            Buchungsart_ID INTEGER NOT NULL,
            Kategorie_ID INTEGER,
            Bemerkung TEXT,
            FOREIGN KEY (IBAN_Auftragskonto) 
                REFERENCES Konto(IBAN)
                ON DELETE CASCADE,
            FOREIGN KEY (Buchungsart_ID) 
                REFERENCES Buchungsart(ID),
            FOREIGN KEY (Kategorie_ID) 
                REFERENCES Kategorie(ID)
        )""")

        connection.execute("CREATE INDEX IF NOT EXISTS idx_konto_kontoinhaber ON Konto(Kontoinhaber_ID)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_transaktion_konto ON Transaktion(IBAN_Auftragskonto)")


def __insert_test_data():
    with sqlite3.connect(__db_path) as connection:
        connection.execute("""INSERT INTO Kontoinhaber (Vorname, Nachname, Email, Passwort) VALUES
                                    ('Max', 'Mustermann', 'max.mustermann@example.com', 'hashpass1'),
                                    ('Lisa', 'Müller', 'lisa.mueller@example.com', 'hashpass2'),
                                    ('Tom', 'Schmidt', 'tom.schmidt@example.com', 'hashpass3')""")
        connection.execute("""INSERT INTO Konto (IBAN, BIC, Bank_Name, Konto_Name, Kontoinhaber_ID, Saldo, Waehrung) VALUES
                                    ('DE89370400440532013000', 'COBADEFFXXX', 'Commerzbank', 'Girokonto Max', 1, 1500.00, 'EUR'),
                                    ('DE75512108001245126199', 'BYLADEM1001', 'Bayerische Bank', 'Sparbuch Lisa', 2, 3200.50, 'EUR'),
                                    ('DE12500105170648489890', 'INGDDEFFXXX', 'ING', 'Girokonto Tom', 3, 800.75, 'EUR')""")
        connection.execute("""INSERT INTO Buchungsart (Buchungsart) VALUES
                                    ('Überweisung'),
                                    ('Lastschrift'),
                                    ('Gutschrift'),
                                    ('Dauerauftrag')""")
        connection.execute("""INSERT INTO Kategorie (Bezeichnung, Kontoinhaber_ID) VALUES
                                    ('Essen', 1),
                                    ('Miete', 1),
                                    ('Einkauf', 2),
                                    ('Freizeit', 2),
                                    ('Reisen', 3)""")
        connection.execute("""INSERT INTO Transaktion (IBAN_Auftragskonto, IBAN_Zahlungsbeteiligter, Name_Zahlungsbeteiligter, Verwendungszweck, Betrag, Saldo_nach_Buchung, Transaktions_Datum, Buchungsart_ID, Kategorie_ID, Bemerkung) VALUES
                                    ('DE89370400440532013000', 'DE75512108001245126199', 'Lisa Müller', 'Miete Februar', 800.00, 700.00, '2026-03-01', 1, 2, 'Monatsmiete'),
                                    ('DE75512108001245126199', 'DE12500105170648489890', 'Tom Schmidt', 'Einkauf Supermarkt', 120.50, 3080.00, '2026-03-03', 2, 3, 'Lebensmittel'),
                                    ('DE12500105170648489890', 'DE89370400440532013000', 'Max Mustermann', 'Freizeitpark', 50.75, 750.00, '2026-03-05', 1, 5, 'Tag im Freizeitpark'),
                                    ('DE89370400440532013000', 'DE12500105170648489890', 'Tom Schmidt', 'Gehalt März', 2000.00, 2700.00, '2026-03-07', 3, NULL, 'Gutschrift vom Arbeitgeber'),
                                    ('DE75512108001245126199', 'DE89370400440532013000', 'Max Mustermann', 'Restaurantbesuch', 60.00, 3020.00, '2026-03-08', 1, 4, 'Abendessen')""")
        connection.commit()

__db_path = "Database.db"

if __name__ == "__main__":
    # __create_Database()
    # __insert_test_data()
    get_users()
    pass