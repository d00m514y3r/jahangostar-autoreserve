# def check_table_exists(cursor, table):
#     cursor.excecute(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'f{table}'")
import sqlite3
import csv
from box import Box

class dbClass(object):
    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        with open("db/texts.csv", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            self.texts = Box({row[0]:row[1] for row in reader})
    
    def create_user(self, user_id, name, self_username, self_password, is_verified, cookie):
        #(user_id, name, self_username, self_password, is_verified)
        x = f"INSERT INTO users VALUES \
        ({user_id}, '{name}', '{self_username}', '{self_password}',\
             '{'TRUE' if is_verified else 'FALSE'}', '{cookie}', '[]')"
        self.cursor.execute(x)
        self.connection.commit()
    
    def get_user(self, user_id):
        x = self.cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}").fetchone()
        if x:
            return {
                "user_id": x[0],
                "name": x[1],
                "self_username": x[2],
                "self_password": x[3],
                "is_verified": x[4],
                "cookie": x[5],
                "filters": x[6]
            }
        return None
    
    def delete_user(self, user_id):
        self.cursor.execute(f"DELETE FROM users WHERE user_id={user_id}")
        self.connection.commit()
    
    def update_cookie(self, user_id, cookie):
        self.cursor.execute(f"UPDATE users SET login_cookie='{cookie}' WHERE user_id={user_id}")
        self.connection.commit()
    
    def update_filters(self, user_id, filters):
        self.cursor.execute(f"UPDATE users SET filters='{filters}' WHERE user_id={user_id}")
        self.connection.commit()

    def reset_db(self):
        # self.cursor.execute("PRAGMA writable_schema = 1")
        # self.cursor.execute("DELETE FROM sqlite_master")
        # self.cursor.execute("PRAGMA writable_schema = 0")
        # self.connection.commit()
        # self.connection("VACUUM")
        # self.connection.commit()
        # self.cursor.execute("PRAGMA integrity_check")
        # self.cursor.execute('PRAGMA encoding="UTF-8"')
        # self.connection.commit()
        try:
            self.cursor.execute("DROP TABLE users")
            print("cleared database")
        except Exception as e:
            print(f"error: {e}")

        self.create_tables()
        #self.connection.commit()

    def create_tables(self):
        # user table
        #primary_key INTEGER PRIMARY KEY,
        self.cursor.execute(
            """CREATE TABLE users(
                
                user_id INTEGER NOT NULL UNIQUE PRIMARY KEY,
                name TEXT NOT NULL,
                self_username TEXT,
                self_password TEXT,
                is_verified bool,
                login_cookie TEXT
                filters TEXT NOT NULL
                )"""
    )
