import sqlite3
import sys
from contextlib import closing
from dtos import *

def execute_select_dto_list(sql:str,dto_class): # sql und den Datentype bzw. die DTO Klasse
    with sqlite3.connect(__db_path) as connection:  # Connection automatisch schließen
        connection.row_factory = sqlite3.Row
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

def execute_select_dto(sql:str,dto_class): # sql und den Datentype bzw. die DTO Klasse
    with sqlite3.connect(__db_path) as connection:  # Connection automatisch schließen
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql)
            column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
            row =  cursor.fetchone() # daten vom select holen
            row_dict = dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben
            return dto_class(**row_dict)  # alle zeilen vom dictionary der DTO Klasse hinzufügen
                                                    # anhand der spalten namen von select und DTO Variablen namen 
                                                    # => namen müssen gleich sein

# def execute_select_dict_list(sql:str) -> dict: # sql und den Datentype bzw. die DTO Klasse
#     with sqlite3.connect(__db_path__) as connection:  # Connection automatisch schließen
#         connection.row_factory = sqlite3.Row
#         with closing(connection.cursor()) as cursor:
#             cursor.execute(sql)
#             column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
#             results = []
#             for row in cursor.fetchall(): # alle daten vom select holen
#                 results.append(dict(zip(column_names, row))) # Spaltennamen mit spaltendaten in dictionary schreiben
#             return results

# def execute_select_dict(sql:str) -> dict: # sql und den Datentype bzw. die DTO Klasse
#     with sqlite3.connect(__db_path__) as connection:  # Connection automatisch schließen
#         connection.row_factory = sqlite3.Row
#         with closing(connection.cursor()) as cursor:
#             cursor.execute(sql)
#             column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
#             row = cursor.fetchone() # alle daten vom select holen
#             return dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben

def execute_select_value(sql:str): # sql und den Datentype bzw. die DTO Klasse
    with sqlite3.connect(__db_path) as connection:  # Connection automatisch schließen
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql)
            row = cursor.fetchone() # alle daten vom select holen
            return row[0]

def execcute_insert_dto():
    pass

def execute_insert_single(sql:str,value):
    with sqlite3.connect(__db_path) as connection:  # Connection automatisch schließen
        connection.row_factory = sqlite3.Row
        with closing(connection.cursor()) as cursor:
            cursor.execute(sql)

def execute_insert_list(sql:str,values:list[list]):
    pass

def get_users():
    # sql = "SELECT id, surname, first_name, creation_date FROM user"
    sql = "create table user"
    users = execute_select_dto_list(sql,UserDTO)
    user = execute_select_dto(sql,UserDTO)
    # value_select = execute_select_value("SELECT id FROM user where id = '1'")
    print(users)

def __create_Database():
    with sqlite3.connect(__db_path) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS Kontoinhaber (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Vorname VARCHAR(100) NOT NULL,
            Nachname VARCHAR(100) NOT NULL,
            Email VARCHAR(150) NOT NULL UNIQUE,
            Passwort VARCHAR(255) NOT NULL)""")
        
        connection.execute("""CREATE TABLE IF NOT EXISTS Konto (
            IBAN VARCHAR(34) PRIMARY KEY,
            BIC VARCHAR(20) NOT NULL,
            Bank_Name VARCHAR(100) NOT NULL,
            Konto_Name VARCHAR(100) NOT NULL,
            Kontoinhaber_ID INT NOT NULL,
            Saldo DECIMAL(15,2) NOT NULL DEFAULT 0,
            Waehrung VARCHAR(10) NOT NULL,
                           
            FOREIGN KEY (Kontoinhaber_ID) 
                REFERENCES Kontoinhaber(ID)
                ON DELETE CASCADE)""")
        
        connection.execute("""CREATE TABLE IF NOT EXISTS Buchungsart (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Buchungsart VARCHAR(100) NOT NULL UNIQUE)""")
        
        connection.execute("""CREATE TABLE IF NOT EXISTS Kategorie (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Bezeichnung VARCHAR(100) NOT NULL,
            Kontoinhaber_ID INT NOT NULL,

            UNIQUE (Bezeichnung, Kontoinhaber_ID),

            FOREIGN KEY (Kontoinhaber_ID)
                REFERENCES Kontoinhaber(ID)
                ON DELETE CASCADE)""")
        
        connection.execute("""CREATE TABLE IF NOT EXISTS Transaktion (
            ID INT AUTO_INCREMENT PRIMARY KEY,

            IBAN_Auftragskonto VARCHAR(34) NOT NULL,
            IBAN_Zahlungsbeteiligter VARCHAR(34) NOT NULL,
            Name_Zahlungsbeteiligter VARCHAR(150) NOT NULL,

            Verwendungszweck VARCHAR(255),

            Betrag DECIMAL(15,2) NOT NULL,
            Saldo_nach_Buchung DECIMAL(15,2) NOT NULL,

            Transaktions_Datum DATE NOT NULL,

            Buchungsart_ID INT NOT NULL,
            Kategorie_ID INT,

            Bemerkung VARCHAR(255),

            FOREIGN KEY (IBAN_Auftragskonto) 
                REFERENCES Konto(IBAN)
                ON DELETE CASCADE,

            FOREIGN KEY (Buchungsart_ID) 
                REFERENCES Buchungsart(ID),

            FOREIGN KEY (Kategorie_ID) 
                REFERENCES Kategorie(ID))""")
        
        connection.execute("""CREATE INDEX idx_konto_kontoinhaber ON Konto(Kontoinhaber_ID)""")
        connection.execute("""CREATE INDEX idx_transaktion_konto ON Transaktion(IBAN_Auftragskonto)""")

__db_path = "Database.db"

if __name__ == "__main__":
    # __create_Database()
    pass