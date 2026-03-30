import sqlite3
import sys
from contextlib import closing
from dtos import *

def get_dto_data(dto:object): # Daten aus dto lesen und zurück geben
    table_name = dto.__class__.__name__[:dto.__class__.__name__.find("DTO")] # Holt sich aus der DTO den Namen der Klasse und schneidet DTO ab am ende
    fields_to_insert = []
    values = {} # values ist ein dictionary und enthält die werte
    for key, value in dto.__dict__.items(): # variablen aus DTO holen
        fields_to_insert.append(key)
        values[key] = value
    return table_name,fields_to_insert,values

def get_table_primary_keys(connection,table_name) ->list[str]:
    tabel_info = connection.execute(f"PRAGMA table_info({table_name})")
    pk_names = []
    for column in tabel_info:
        if column[5] > 0: # in column 5 steht drin ob es ein teil des PK ist 0=kein teil, 0< ist teil des pk (1=Teil 1, 2= Teil2 ... des PK)
            pk_names.append(column[1])
    return pk_names

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
    return execute_select_dto_list(sql,dto_class)[0]
    # with sqlite3.connect(__db_path) as connection:
    #     connection.execute("PRAGMA foreign_keys = ON;") 
    #     connection.row_factory = sqlite3.Row
    #     with closing(connection.cursor()) as cursor:
    #         cursor.execute(sql)
    #         column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
    #         row =  cursor.fetchone() # daten vom select holen
    #         row_dict = dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben
    #         return dto_class(**row_dict)  # alle zeilen vom dictionary der DTO Klasse hinzufügen
    #                                                 # anhand der spalten namen von select und DTO Variablen namen 
    #                                                 # => namen müssen gleich sein

def execute_select_value(sql:str) -> str|int|float: # sql und den Datentype bzw. die DTO Klasse
    with sqlite3.connect(__db_path) as connection:  # Connection automatisch schließen
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql)
            row = cursor.fetchone() # daten vom select holen
            return row[0]
        
def execute_insert_dtos(dtos:object | list[object]):
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        if not isinstance(dtos, list):
            dtos = [dtos]
        try:
            for dto in dtos:
                table_name,fields_to_insert,values = get_dto_data(dto) # Daten aus DTO lesen
                # ID entfernen da diese autonicrementet werden
                fields_to_insert.remove("ID")
                del values["ID"]
                # sql mit Named Parametern (z.b. insert table(name,email) values (:Name, :Email))
                sql = f"INSERT INTO {table_name} ({', '.join(fields_to_insert)}) VALUES ({', '.join([":" + p for p in fields_to_insert])})"
                connection.execute(sql, values)
            connection.commit()
        except sqlite3.DatabaseError as e:
            connection.rollback()
            print("DB Fehler:", e)
            raise
            
def execute_update_dtos(dtos:object | list[object]):
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        if not isinstance(dtos, list):
            dtos = [dtos]
        try:
            for dto in dtos:
                table_name,fields_to_insert,values = get_dto_data(dto)
                update_values = []
                for column in fields_to_insert:
                    update_values.append(column + "=:" + column)
                
                primary_keys = get_table_primary_keys(connection,table_name)
                where_values= []
                for column in primary_keys:
                    where_values.append(column + "=:" + column)
                sql = f"UPDATE {table_name} set {', '.join(update_values)} where {' and '.join(where_values)}"
                connection.execute(sql,values)
            connection.commit()
        except sqlite3.DatabaseError as e:
            connection.rollback()
            print("DB Fehler:", e)
            raise

def get_users():
    sql = "SELECT * FROM Kontoinhaber"
    users = execute_select_dto_list(sql,KontoinhaberDTO)
    return users

def __create_Database():
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")

        # ---------------- BANK ----------------
        connection.execute("""
        CREATE TABLE IF NOT EXISTS Bank (
            BLZ TEXT PRIMARY KEY,
            Name TEXT NOT NULL
        )""")

        # ---------------- WAEHRUNG ----------------
        connection.execute("""
        CREATE TABLE IF NOT EXISTS Waehrung (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Waehrung TEXT NOT NULL UNIQUE
        )""")

        # ---------------- KONTOINHABER ----------------
        connection.execute("""
        CREATE TABLE IF NOT EXISTS Kontoinhaber (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Vorname TEXT NOT NULL,
            Nachname TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE,
            Passwort TEXT NOT NULL
        )""")

        # ---------------- KONTO ----------------
        connection.execute("""
        CREATE TABLE IF NOT EXISTS Konto (
            IBAN TEXT PRIMARY KEY,
            BIC TEXT NOT NULL,
            BLZ TEXT NOT NULL,
            Konto_Name TEXT NOT NULL,
            Kontoinhaber_ID INTEGER NOT NULL,
            Saldo REAL NOT NULL DEFAULT 0,
            Waehrung_ID INTEGER NOT NULL,

            FOREIGN KEY (BLZ)
                REFERENCES Bank(BLZ),

            FOREIGN KEY (Kontoinhaber_ID)
                REFERENCES Kontoinhaber(ID)
                ON DELETE CASCADE,

            FOREIGN KEY (Waehrung_ID)
                REFERENCES Waehrung(ID)
        )""")

        # ---------------- BUCHUNGSART ----------------
        connection.execute("""
        CREATE TABLE IF NOT EXISTS Buchungsart (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Buchungsart TEXT NOT NULL UNIQUE
        )""")

        # ---------------- KATEGORIE ----------------
        connection.execute("""
        CREATE TABLE IF NOT EXISTS Kategorie (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Bezeichnung TEXT NOT NULL,
            Kontoinhaber_ID INTEGER NOT NULL,

            UNIQUE (Bezeichnung, Kontoinhaber_ID),

            FOREIGN KEY (Kontoinhaber_ID)
                REFERENCES Kontoinhaber(ID)
                ON DELETE CASCADE
        )""")

        # ---------------- TRANSAKTION ----------------
        connection.execute("""
        CREATE TABLE IF NOT EXISTS Transaktion (
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

        # ---------------- INDIZES ----------------
        connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_konto_kontoinhaber 
        ON Konto(Kontoinhaber_ID)
        """)

        connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_transaktion_konto 
        ON Transaktion(IBAN_Auftragskonto)
        """)

def __insert_test_data():
    with sqlite3.connect(__db_path) as connection:

        # ---------------- BANK ----------------
        connection.execute("""INSERT INTO Bank (BLZ, Name) VALUES
            ('37040044', 'Commerzbank'),
            ('51210800', 'Bayerische Bank'),
            ('50010517', 'ING')
        """)

        # ---------------- WAEHRUNG ----------------
        connection.execute("""INSERT INTO Waehrung (Waehrung) VALUES
            ('EUR'),
            ('USD')
        """)

        # ---------------- KONTOINHABER ----------------
        connection.execute("""INSERT INTO Kontoinhaber (Vorname, Nachname, Email, Passwort) VALUES
            ('Max', 'Mustermann', 'max.mustermann@example.com', 'hashpass1'),
            ('Lisa', 'Müller', 'lisa.mueller@example.com', 'hashpass2'),
            ('Tom', 'Schmidt', 'tom.schmidt@example.com', 'hashpass3')
        """)

        # ---------------- KONTO ----------------
        connection.execute("""INSERT INTO Konto 
            (IBAN, BIC, BLZ, Konto_Name, Kontoinhaber_ID, Saldo, Waehrung_ID) VALUES
            ('DE89370400440532013000', 'COBADEFFXXX', '37040044', 'Girokonto Max', 1, 1500.00, 1),
            ('DE75512108001245126199', 'BYLADEM1001', '51210800', 'Sparbuch Lisa', 2, 3200.50, 1),
            ('DE12500105170648489890', 'INGDDEFFXXX', '50010517', 'Girokonto Tom', 3, 800.75, 1)
        """)

        # ---------------- BUCHUNGSART ----------------
        connection.execute("""INSERT INTO Buchungsart (Buchungsart) VALUES
            ('Überweisung'),
            ('Lastschrift'),
            ('Gutschrift'),
            ('Dauerauftrag')
        """)

        # ---------------- KATEGORIE ----------------
        connection.execute("""INSERT INTO Kategorie (Bezeichnung, Kontoinhaber_ID) VALUES
            ('Essen', 1),
            ('Miete', 1),
            ('Einkauf', 2),
            ('Freizeit', 2),
            ('Reisen', 3)
        """)

        # ---------------- TRANSAKTION ----------------
        connection.execute("""INSERT INTO Transaktion 
            (IBAN_Auftragskonto, IBAN_Zahlungsbeteiligter, Name_Zahlungsbeteiligter, 
             Verwendungszweck, Betrag, Saldo_nach_Buchung, Transaktions_Datum, 
             Buchungsart_ID, Kategorie_ID, Bemerkung) VALUES

            ('DE89370400440532013000', 'DE75512108001245126199', 'Lisa Müller', 
             'Miete Februar', 800.00, 700.00, '2026-03-01', 1, 2, 'Monatsmiete'),

            ('DE75512108001245126199', 'DE12500105170648489890', 'Tom Schmidt', 
             'Einkauf Supermarkt', 120.50, 3080.00, '2026-03-03', 2, 3, 'Lebensmittel'),

            ('DE12500105170648489890', 'DE89370400440532013000', 'Max Mustermann', 
             'Freizeitpark', 50.75, 750.00, '2026-03-05', 1, 5, 'Tag im Freizeitpark'),

            ('DE89370400440532013000', 'DE12500105170648489890', 'Tom Schmidt', 
             'Gehalt März', 2000.00, 2700.00, '2026-03-07', 3, NULL, 'Gutschrift Arbeitgeber'),

            ('DE75512108001245126199', 'DE89370400440532013000', 'Max Mustermann', 
             'Restaurantbesuch', 60.00, 3020.00, '2026-03-08', 1, 4, 'Abendessen')
        """)

        connection.commit()

__db_path = "./src/Database.db"

if __name__ == "__main__":
    # __create_Database()
    # __insert_test_data()
    user = [KontoinhaberDTO(ID=4,Vorname="Kevin",Nachname="Test_neu",Email="kevin.mustermax@web.de",Passwort="abc123")]
    # execute_insert_dtos(user)
    # execute_update_dtos(user)
    users = get_users()
    for user in users:
        print(user)
