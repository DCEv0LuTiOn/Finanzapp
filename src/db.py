from shlex import join
import sqlite3
import sys
from contextlib import closing
from tkinter import LEFT
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

def execute_select_dto_list(sql:str,dto_class,wheres:dict) -> list[object]: # sql und den Datentype bzw. die DTO Klasse
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;") # wird von sqlight3 benötigt das forgein_keys funktionieren
        connection.row_factory = sqlite3.Row            # wird von sqlight3 benötigt das man spaltennamen im cursor mit cursor.description rauslesen kann
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql,wheres)
            print(sql)
            print(wheres)
            column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
            results = []
            for row in cursor.fetchall(): # alle daten vom select holen
                row_dict = dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben
                results.append(dto_class(**row_dict))  # alle zeilen vom dictionary der DTO Klasse hinzufügen
                                                    # anhand der spalten namen von select und DTO Variablen namen 
                                                    # => namen müssen gleich sein
            return results

def execute_select_dto(sql:str,dto_class,wheres:dict) -> object: # sql und den Datentype bzw. die DTO Klasse
    executed_list = execute_select_dto_list(sql,dto_class,wheres)
    if len(executed_list) > 0:
        return executed_list[0]
    else:
        return None

def execute_select_value(sql:str,wheres:dict) -> str|int|float: # sql und den Datentype bzw. die DTO Klasse
    with sqlite3.connect(__db_path) as connection:  # Connection automatisch schließen
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql,wheres)
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
                if "ID" in fields_to_insert:
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

def execute_delete_dtos(dtos: object | list[object]):
    with sqlite3.connect(__db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        if not isinstance(dtos, list):
            dtos = [dtos]
        try:
            for dto in dtos:
                table_name, fields, values = get_dto_data(dto)
                primary_keys = get_table_primary_keys(connection, table_name)
                if not primary_keys:
                    raise ValueError(f"Tabelle {table_name} hat keine Primärschlüssel. Löschen nicht sicher möglich.")
                # WHERE-Bedingung auf Basis der Primärschlüssel bauen
                # Ergebnis: ["ID=:ID"] oder ["ID1=:ID1", "ID2=:ID2"] bei zusammengesetzten Keys
                where_clauses = [f"{column}=:{column}" for column in primary_keys]
                
                sql = f"DELETE FROM {table_name} WHERE {' AND '.join(where_clauses)}"
                connection.execute(sql, values)
            connection.commit()
            
        except sqlite3.DatabaseError as e:
            connection.rollback()
            print("DB Fehler beim Löschen:", e)
            raise


def get_user_by_email(email):
    wheres = {'Email':email}
    sql = "SELECT * FROM Kontoinhaber where Email = :Email"
    users = execute_select_dto(sql,KontoinhaberDTO,wheres)
    return users

def get_user_by_id(user_id) -> KontoinhaberDTO:
    wheres = {'ID':user_id}
    sql = "SELECT * FROM Kontoinhaber where ID = :ID"
    user = execute_select_dto(sql,KontoinhaberDTO,wheres)
    return user

def get_konto_by_user_id(kontoinhaber_id) -> list[KontoDTO]:
    wheres = {'Kontoinhaber_ID':kontoinhaber_id}
    sql = "SELECT * FROM Konto where Kontoinhaber_ID = :Kontoinhaber_ID"
    konten = execute_select_dto_list(sql,KontoDTO,wheres)
    return konten

def get_konto_by_iban(iban) -> KontoDTO:
    wheres = {'IBAN':iban}
    sql = "SELECT * FROM Konto where IBAN = :IBAN"
    konto = execute_select_dto(sql,KontoDTO,wheres)
    return konto

def get_Transaktionen_by_konto_iban(iban) -> list[TransaktionDTO]:
    wheres = {'IBAN_Auftragskonto':iban}
    sql = "SELECT * FROM Transaktion where IBAN_Auftragskonto = :IBAN_Auftragskonto"
    transaktionen = execute_select_dto_list(sql,TransaktionDTO,wheres)
    return transaktionen

def get_transaktion_by_id(transaktion_id) -> TransaktionDTO:
    wheres = {'ID':transaktion_id}
    sql = "SELECT * FROM Transaktion where ID = :ID"
    transaktion_dto = execute_select_dto(sql,TransaktionDTO,wheres)
    return transaktion_dto

def get_Transaktionen_by_kategorie_id(kategorie_id) -> list[TransaktionDTO]:
    wheres = {'Kategorie_ID':kategorie_id}
    sql = "SELECT * FROM Transaktion where Kategorie_ID = :Kategorie_ID"
    transaktionen = execute_select_dto_list(sql,TransaktionDTO,wheres)
    return transaktionen

def get_kategorien_by_kontoinhaber_id(kontoinhaber_id) -> list[KategorieDTO]:
    wheres = {'Kontoinhaber_ID':kontoinhaber_id}
    sql = "SELECT * FROM Kategorie where Kontoinhaber_ID = :Kontoinhaber_ID"
    kategorien = execute_select_dto_list(sql,KategorieDTO,wheres)
    return kategorien
def get_all_konten_by_kontoinhaber_id(kontoinhaber_id) -> list[KontoDTO]:
    wheres = {'Kontoinhaber_ID':kontoinhaber_id}
    sql = "SELECT * FROM Konto where Kontoinhaber_ID = :Kontoinhaber_ID"
    konten = execute_select_dto_list(sql,KontoDTO,wheres)
    return konten

def get_id_by_waehrung(waehrung) -> WaehrungDTO:
    wheres = {'Waehrung':waehrung}
    sql = "SELECT * FROM Waehrung where Waehrung = :Waehrung"
    waehrung_dto = execute_select_dto(sql,WaehrungDTO,wheres)
    return waehrung_dto

def get_all_waehrungen() -> list[WaehrungDTO]:
    sql = "SELECT * FROM Waehrung"
    waehrungen = execute_select_dto_list(sql,WaehrungDTO,{})
    return waehrungen

def get_id_by_buchungsart(buchungsart) -> BuchungsartDTO:
    wheres = {'Buchungsart':buchungsart}
    sql = "SELECT * FROM Buchungsart where Buchungsart = :Buchungsart"
    buchungsart_dto = execute_select_dto(sql,BuchungsartDTO,wheres)
    return buchungsart_dto

def get_all_buchungsarten() -> list[BuchungsartDTO]:
    sql = "SELECT * FROM Buchungsart"
    buchungsarten = execute_select_dto_list(sql,BuchungsartDTO,{})
    return buchungsarten

def get_id_by_kategorie(bezeichnung, kontoinhaber_id) -> KategorieDTO:
    wheres = {'Bezeichnung':bezeichnung, 'Kontoinhaber_ID':kontoinhaber_id}
    sql = "SELECT * FROM Kategorie where Bezeichnung = :Bezeichnung and Kontoinhaber_ID = :Kontoinhaber_ID"
    kategorie_dto = execute_select_dto(sql,KategorieDTO,wheres)
    return kategorie_dto

def get_kategorie_by_id(kategorie_id) -> KategorieDTO:
    wheres = {'ID':kategorie_id}
    sql = "SELECT * FROM Kategorie where ID = :ID"
    kategorie_dto = execute_select_dto(sql,KategorieDTO,wheres)
    return kategorie_dto

def get_bank_by_blz(blz) -> BankDTO:
    wheres = {'BLZ':blz}
    sql = "SELECT * FROM Bank where BLZ = :BLZ"
    bank_dto = execute_select_dto(sql,BankDTO,wheres)
    return bank_dto

def get_filtered_transaktionen(transaktion_filter: TransaktionDTO, user_id: int, datumBis: str, selected_konten: list[str] = None, selected_kategorien: list[str] = None) -> list[DataInputDTOView]:
    wheres = {"user_id": user_id}
    if len(selected_konten) == 0:
        return []
    
    # Basis-SQL
    sql = """
        SELECT t.ID, t.IBAN_Auftragskonto, t.IBAN_Zahlungsbeteiligter, t.Name_Zahlungsbeteiligter, 
               t.Verwendungszweck, t.Betrag, t.Saldo_nach_Buchung, t.Transaktions_Datum, 
               t.Bemerkung, t.Kategorie_ID, k2.Bezeichnung as Kategorie, t.Buchungsart_ID, b.Buchungsart 
        FROM Kontoinhaber i 
        JOIN Konto k ON i.ID = k.Kontoinhaber_ID 
        JOIN Transaktion t ON k.IBAN = t.IBAN_Auftragskonto 
        LEFT JOIN Kategorie k2 ON t.Kategorie_ID = k2.ID AND i.ID = k2.Kontoinhaber_ID 
        LEFT JOIN Buchungsart b ON t.Buchungsart_ID = b.ID 
        WHERE i.ID = :user_id
    """

    # 1. MULTI-SELECT: Konten & Kategorien (Logik bleibt gleich)
    if selected_konten:
        iban_params = {f"ib_{i}": iban for i, iban in enumerate(selected_konten)}
        iban_placeholders = ", ".join([f":{k}" for k in iban_params.keys()])
        sql += f" AND t.IBAN_Auftragskonto IN ({iban_placeholders})"
        wheres.update(iban_params)

    if selected_kategorien:
        clean_kategorie_ids = [k for k in selected_kategorien if k != "null" and str(k).strip() != ""]
        has_null = "null" in selected_kategorien
        kat_conditions = []
        if clean_kategorie_ids:
            kat_params = {f"kat_{i}": kid for i, kid in enumerate(clean_kategorie_ids)}
            kat_placeholders = ", ".join([f":{k}" for k in kat_params.keys()])
            kat_conditions.append(f"t.Kategorie_ID IN ({kat_placeholders})")
            wheres.update(kat_params)
        if has_null:
            kat_conditions.append("t.Kategorie_ID IS NULL")
        if kat_conditions:
            sql += f" AND ({' OR '.join(kat_conditions)})"

    # 2. Klassische Filter (ID, Zweck, Betrag)
    if transaktion_filter.ID and str(transaktion_filter.ID).strip() not in ["", "0"]:
        sql += " AND t.ID = :id"
        wheres["id"] = transaktion_filter.ID

    if transaktion_filter.Verwendungszweck and transaktion_filter.Verwendungszweck.strip():
        sql += " AND t.Verwendungszweck LIKE :Verwendungszweck"
        wheres["Verwendungszweck"] = f"%{transaktion_filter.Verwendungszweck.strip()}%"

    if transaktion_filter.Betrag and str(transaktion_filter.Betrag).strip() != "":
        sql += " AND t.Betrag = :Betrag"
        wheres["Betrag"] = transaktion_filter.Betrag

    # --- NEU: Saldo Filter ---
    if transaktion_filter.Saldo_nach_Buchung and str(transaktion_filter.Saldo_nach_Buchung).strip() != "":
        sql += " AND t.Saldo_nach_Buchung = :Saldo"
        wheres["Saldo"] = transaktion_filter.Saldo_nach_Buchung

    # --- NEU: IBAN & Name Beteiligter ---
    if transaktion_filter.IBAN_Zahlungsbeteiligter and transaktion_filter.IBAN_Zahlungsbeteiligter.strip():
        sql += " AND t.IBAN_Zahlungsbeteiligter LIKE :iban_bet"
        wheres["iban_bet"] = f"%{transaktion_filter.IBAN_Zahlungsbeteiligter.strip()}%"

    if transaktion_filter.Name_Zahlungsbeteiligter and transaktion_filter.Name_Zahlungsbeteiligter.strip():
        sql += " AND t.Name_Zahlungsbeteiligter LIKE :name_bet"
        wheres["name_bet"] = f"%{transaktion_filter.Name_Zahlungsbeteiligter.strip()}%"

    # --- NEU: Buchungsart & Bemerkung ---
    if transaktion_filter.Buchungsart_ID and str(transaktion_filter.Buchungsart_ID).strip() not in ["", "0"]:
        sql += " AND t.Buchungsart_ID = :art_id"
        wheres["art_id"] = transaktion_filter.Buchungsart_ID

    if transaktion_filter.Bemerkung and transaktion_filter.Bemerkung.strip():
        sql += " AND t.Bemerkung LIKE :Bemerkung"
        wheres["Bemerkung"] = f"%{transaktion_filter.Bemerkung.strip()}%"

    # 3. Datums-Logik (Von - Bis)
    datum_von = transaktion_filter.Transaktions_Datum
    has_von = datum_von and str(datum_von).strip() != ""
    has_bis = datumBis and str(datumBis).strip() != "" and datumBis != "0000-00-00"

    if has_von and has_bis:
        sql += " AND t.Transaktions_Datum BETWEEN :Transaktions_Datum_von AND :Transaktions_Datum_bis"
        wheres["Transaktions_Datum_von"] = datum_von
        wheres["Transaktions_Datum_bis"] = datumBis
    elif has_von:
        sql += " AND t.Transaktions_Datum = :Transaktions_Datum_von"
        wheres["Transaktions_Datum_von"] = datum_von

    sql += " ORDER BY t.Transaktions_Datum DESC"

    print(sql) # Debug-Ausgabe des finalen SQL-Befehls
    
    return execute_select_dto_list(sql, DataInputDTOView, wheres)

def get_transaktionen_by_IBANs_and_Kategorie_IDs_and_date(ibans:list[str], kategorie_IDs:list, start_date:str, end_date:str) -> list[TransaktionDTO]:

    # 1. Validierung: Wenn nichts gewählt ist, sofort abbrechen
    if not ibans or not kategorie_IDs:
        return []

    # 2. Daten-Vorbereitung: Erstelle eine saubere Liste nur mit IDs (Integers)
    # Filtert "null" raus und behält alles andere
    clean_kategorie_ids = [k for k in kategorie_IDs if k != "null"]
    has_null = "null" in kategorie_IDs

    # 3. IBAN Platzhalter generieren (für SQLite Einzelparameter)
    iban_params = {f"ib_{i}": val for i, val in enumerate(ibans)}
    iban_placeholders = ", ".join([f":{k}" for k in iban_params.keys()])

    # Start des SQL-Befehls mit Datumsfiltern
    sql = f"""
    SELECT * FROM Transaktion 
    WHERE IBAN_Auftragskonto IN ({iban_placeholders})
      AND (:start_date = '' OR Transaktions_Datum >= :start_date)
      AND (:end_date = '' OR Transaktions_Datum <= :end_date)
    """

    # 4. Kategorie-Logik mit der "cleanen" Liste
    kat_params = {}
    if clean_kategorie_ids:
        # Platzhalter für die echten IDs bauen
        kat_params = {f"kat_{i}": val for i, val in enumerate(clean_kategorie_ids)}
        kat_placeholders = ", ".join([f":{k}" for k in kat_params.keys()])

        if has_null:
            sql += f" AND (Kategorie_ID IN ({kat_placeholders}) OR Kategorie_ID IS NULL)"
        else:
            sql += f" AND Kategorie_ID IN ({kat_placeholders})"
    elif has_null:
        # NUR "null" wurde ausgewählt, keine anderen IDs
        sql += " AND Kategorie_ID IS NULL"

    # 5. Alle Parameter für execute_select_dto_list zusammenführen
    wheres = {
        **iban_params,
        **kat_params,
        'start_date': start_date,
        'end_date': end_date
    }

    print(sql) # Debug-Ausgabe des finalen SQL-Befehls

    return execute_select_dto_list(sql, TransaktionDTO, wheres)

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
    # # __insert_test_data()
    # konten = get_konto_by_user_id(2)
    # for konto in konten:
    #     konto.Konto_Name = "Sparbuch"
    #     konto.Kontoinhaber_ID = 8
    #     execute_update_dtos(konto)
    # kategorie:list[KategorieDTO] = [KategorieDTO(Bezeichnung="Essen", Kontoinhaber_ID=8),
    #                                     KategorieDTO(Bezeichnung="Miete", Kontoinhaber_ID=8),
    #                                     KategorieDTO(Bezeichnung="Einkauf", Kontoinhaber_ID=8),
    #                                     KategorieDTO(Bezeichnung="Freizeit", Kontoinhaber_ID=8),
    #                                     KategorieDTO(Bezeichnung="Reisen", Kontoinhaber_ID=8),
    #                                     KategorieDTO(Bezeichnung="Auto", Kontoinhaber_ID=8),
    #                                     KategorieDTO(Bezeichnung="Sonstiges", Kontoinhaber_ID=8)]
    # execute_insert_dtos(kategorie)
    # test_daten = [
        # TransaktionDTO(None, "DE75512108001245126199", "DE445000000012345678", "Arbeitgeber GmbH test", "Gehalt 03/2026", 2450.00, 5450.00, "2026-03-01", 1, 15, "Sonstiges / Eingang"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE105000000087654321", "Vermieter Wohnen test", "Miete Maerz", -850.00, 1200.50, "2026-03-02", 2, 19, "Miete"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE885000000011223344", "Edeka Center test", "Wocheneinkauf", -45.67, 5404.33, "2026-03-03", 3, 13, "Einkauf"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE225000000099887766", "Stadtwerke test", "Abschlag Strom", -112.00, 1088.50, "2026-03-03", 2, 17, "Sonstiges"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE335000000055443322", "Kino Welt test", "Tickets & Snacks", -29.99, 5374.34, "2026-03-04", 3, 14, "Freizeit"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE555000000066778899", "Lufthansa test", "Flug Buchung", -254.95, 833.55, "2026-03-05", 3, 16, "Reisen"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE775000000012121212", "Shell Station test", "Tanken", -82.50, 5291.84, "2026-03-06", 3, 19, "Auto"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE195000000034343434", "Restaurant Da Luigi test", "Abendessen", -65.00, 768.55, "2026-03-07", 3, 15, "Essen"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE405000000090909090", "Netflixcomt", "Abo", -17.99, 5273.85, "2026-03-08", 3, 13, "Freizeit"),

        # TransaktionDTO(None, "DE12500105170648489890", "DE215000000078787878", "KFZ Versicherungt", "Jahresbeitrag", -412.40, 356.15, "2026-03-09", 2, 14, "Auto"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE305000000056565656", "tRewe Markt", "Einkauf", -63.20, 5210.65, "2026-03-10", 3, 19, "Einkauf"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE445000000012345678", "tArbeitgeber GmbH", "Bonus", 500.00, 856.15, "2026-03-11", 1, 17, "Sonstiges"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE125000000011111111", "tH&M Online", "Kleidung", -89.95, 5120.70, "2026-03-12", 3, 18, "Sonstiges"),

        # TransaktionDTO(None, "DE12500105170648489890", "DE995000000022222222", "tDeutsche Bahn", "Urlaubsreise", -149.00, 707.15, "2026-03-13", 3, 16, "Reisen"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE885000000011223344", "tEdeka Center", "Getraenke", -12.50, 5108.20, "2026-03-14", 3, 15, "Einkauf"),
        # # TransaktionDTO(None, "DE12500105170648489890", "DE775000000012121212", "tShell Station", "Waschanlage", -15.00, 692.15, "2026-03-15", 3, 14, "Auto"),

        # TransaktionDTO(None, "DE75512108001245126199", "DE335000000055443322", "tAmazon.de", "Haushalt", -34.00, 5074.20, "2026-03-16", 3, 13, "Einkauf"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE101010101010101010", "tPizzeria", "Pizza", -25.00, 667.15, "2026-03-17", 3, 19, "Essen"),

        # TransaktionDTO(None, "DE75512108001245126199", "DE505050505050505050", "tSpotify AB", "Entertainment", -14.99, 5059.21, "2026-03-18", 2, 17, "Freizeit"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE305000000056565656", "tRewe Markt", "Snacks", -8.45, 658.70, "2026-03-19", 3, 16, "Einkauf"),

        # TransaktionDTO(None, "DE75512108001245126199", "DE225000000099887766", "tVermieter Garagen", "Stellplatz", -80.00, 4979.21, "2026-03-20", 2, 14, "Miete"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE665000000033333333", "tApotheke", "Medikamente", -22.30, 636.40, "2026-03-21", 3, 13, "Sonstiges"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE111111111111111111", "tIKEA", "Deko", -40.00, 4939.21, "2026-03-22", 3, 15, "Sonstiges"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE445000000012345678", "tArbeitgeber GmbH", "Reisekosten", 125.50, 761.90, "2026-03-23", 1, 17, "Reisen"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE335000000055443322", "tAmazon.de", "Buch", -12.99, 4926.22, "2026-03-24", 3, 16, "Freizeit"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE885000000011223344", "tEdeka Center", "Einkauf", -33.10, 728.80, "2026-03-25", 3, 14, "Einkauf"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE775000000012121212", "tShell Station", "Tanken", -95.00, 4831.22, "2026-03-26", 3, 13, "Auto"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE305000000056565656", "tBurger King", "Essen gehen", -12.50, 716.30, "2026-03-27", 3, 17, "Essen"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE105000000087654321", "tImmobilien GmbH", "Miete Wohnung", -900.00, 3931.22, "2026-03-28", 2, 19, "Miete"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE225000000099887766", "tADAC", "Beitrag", -15.20, 701.10, "2026-03-29", 3, 15, "Auto"),
        # TransaktionDTO(None, "DE12500105170648489890", "DE225000000099887755", "tAbschlepen", "Beitrag", -15.20, 701.10, "2026-03-29", 3, 15, "Auto Abschlepen"),
        # TransaktionDTO(None, "DE75512108001245126199", "DE885000000021223341", "tEdeka Center", "Getraenke", -12.50, 5108.20, "2026-03-14", 3, 14, "Einkauf")
    # ]
    # execute_insert_dtos(test_daten)
    # user = get_user_by_email("test@web.de")
    # user.vorname = "Kevin"
    # user.nachname = "Mustermax"
    # execute_update_dtos(user)
    # users = get_user_by_email("kevin.mustermax@web.de")
    # for user in users:
    #     print(user)
    # kategorien = get_kategorien_by_kontoinhaber_id(8)
    # for kategorie in kategorien:
    #     print(kategorie)
    # konten = get_konto_by_user_id(5)
    # for konto in konten:
    #     print(konto)
    pass
