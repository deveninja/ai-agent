import os
from dotenv import load_dotenv

load_dotenv()


def get_mariadb_connection():
  import mariadb

  return mariadb.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
  )


def get_postgres_connection():
  import psycopg2

  return psycopg2.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME")
  )


def get_mysql_connection():

  import mysql

  return mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
  )


def db_factory(db_type: str):
  switcher = {
      "mariadb": get_mariadb_connection,
      "postgres": get_postgres_connection,
      "mysql": get_mysql_connection,
  }

  db_func = switcher.get(db_type.lower())

  if not db_func:
      raise ValueError(f"Unsupported database type: {db_type}")

  return db_func()