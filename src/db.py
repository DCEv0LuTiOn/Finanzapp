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

# def fetch_all(cursor, dto_class): # cursor mitgeben und den Datentype bzw. die DTO Klasse
#     column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
#     results = []
#     for row in cursor.fetchall(): # alle daten vom select holen
#         row_dict = dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben
#         results.append(dto_class(**row_dict))  # alle zeilen vom dictionary der DTO Klasse hinzufügen
#                                             # anhand der spalten namen von select und DTO Variablen namen 
#                                             # => namen müssen gleich sein
#     return results

# def fetch_single(cursor, dto_class): # cursor mitgeben und den Datentype bzw. die DTO Klasse
#     column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
#     for row in cursor.fetchall(): # alle daten vom select holen
#         row_dict = dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben
#         return dto_class(**row_dict)  # alle zeilen vom dictionary der DTO Klasse hinzufügen
#                                             # anhand der spalten namen von select und DTO Variablen namen 
#                                             # => namen müssen gleich sein

def execute_select_dto_list(sql:str,dto_class): # sql und den Datentype bzw. die DTO Klasse
    with db_connect() as connection: # connection schliesen nach abfrage
        with connection.cursor() as cursor: # cursor schliesen nach abfrage
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
    with db_connect() as connection: # connection schliesen nach abfrage
        with connection.cursor() as cursor: # cursor schliesen nach abfrage
            cursor.execute(sql)
            column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
            row =  cursor.fetchone() # daten vom select holen
            row_dict = dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben
            return dto_class(**row_dict)  # alle zeilen vom dictionary der DTO Klasse hinzufügen
                                                    # anhand der spalten namen von select und DTO Variablen namen 
                                                    # => namen müssen gleich sein

def execute_select_dict_list(sql:str) -> dict: # sql und den Datentype bzw. die DTO Klasse
    with db_connect() as connection: # connection schliesen nach abfrage
        with connection.cursor() as cursor: # cursor schliesen nach abfrage
            cursor.execute(sql)
            column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
            results = []
            for row in cursor.fetchall(): # alle daten vom select holen
                results.append(dict(zip(column_names, row))) # Spaltennamen mit spaltendaten in dictionary schreiben
            return results

def execute_select_dict(sql:str) -> dict: # sql und den Datentype bzw. die DTO Klasse
    with db_connect() as connection: # connection schliesen nach abfrage
        with connection.cursor() as cursor: # cursor schliesen nach abfrage
            cursor.execute(sql)
            column_names = [col[0] for col in cursor.description] # Spaltennamen aus dem select holen
            row = cursor.fetchone() # alle daten vom select holen
            return dict(zip(column_names, row)) # Spaltennamen mit spaltendaten in dictionary schreiben

def execute_select_value(sql:str): # sql und den Datentype bzw. die DTO Klasse
    with db_connect() as connection: # connection schliesen nach abfrage
        with connection.cursor() as cursor: # cursor schliesen nach abfrage
            cursor.execute(sql)
            row = cursor.fetchone() # alle daten vom select holen
            return row[0]

def execcute_insert_dto():
    pass

def execute_insert_single(sql:str,value):
    with db_connect() as connection: # connection schliesen nach abfrage
        with connection.cursor() as cursor: # cursor schliesen nach abfrage
            cursor.execute(sql)

def execute_insert_list(sql:str,values:list[list]):
    pass

def get_users():
    sql = "SELECT id, surname, first_name, creation_date FROM user"
    users = execute_select_dto_list(sql,UserDTO)
    user = execute_select_dto(sql,UserDTO)
    user_dict = execute_select_dict_list(sql)
    value_select = execute_select_value("SELECT id FROM user where id = '1'")
    print(users)

if __name__ == "__main__":
    get_users()