import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error as MySQLError

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")


class OpenDb:
    def __init__(self):
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_DATABASE
        self.connection = None

    def __enter__(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            return self.connection.cursor()
        except MySQLError as e:
            raise RuntimeError(f"Database connection failed: {e.msg}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.connection:
            return

        try:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
        finally:
            self.connection.close()
