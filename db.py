import mariadb
import sys
from dtos import *

def db_connect():
    try:
        connection = mariadb.connect(
            host="localhost",
            user="admin",
            password="admin123",
            database="finanzapp"
        )
        return connection
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)

def fetch_all(cursor, dto_class): # cursor mitgeben und den Datentype bzw. die DTO Klasse
    column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
    results = []
    for row in cursor.fetchall(): # alle daten vom select holen
        row_dict = dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben
        results.append(dto_class(**row_dict))  # alle zeilen vom dictionary der DTO Klasse hinzufügen
                                            # anhand der spalten namen von select und DTO Variablen namen 
                                            # => namen müssen gleich sein
    return results

def fetch_single(cursor, dto_class): # cursor mitgeben und den Datentype bzw. die DTO Klasse
    column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
    for row in cursor.fetchall(): # alle daten vom select holen
        row_dict = dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben
        return dto_class(**row_dict)  # alle zeilen vom dictionary der DTO Klasse hinzufügen
                                            # anhand der spalten namen von select und DTO Variablen namen 
                                            # => namen müssen gleich sein

def execute_select_list(sql:str,dto_class): # sql und den Datentype bzw. die DTO Klasse
    with db_connect() as connection: # connection schliesen nach abfrage
        with connection.cursor() as cursor: # cursor schliesen nach abfrage
            cursor.execute(sql)
            return fetch_all(cursor,dto_class)

def execute_select_single(sql:str,dto_class): # sql und den Datentype bzw. die DTO Klasse
    with db_connect() as connection: # connection schliesen nach abfrage
        with connection.cursor() as cursor: # cursor schliesen nach abfrage
            cursor.execute(sql)
            return fetch_single(cursor,dto_class)

def get_users():
    sql = "SELECT id, surname, first_name, email, creation_date FROM user"
    users = execute_select_list(sql,UserDTO)
    print(users)

if __name__ == "__main__":
    get_users()


    
