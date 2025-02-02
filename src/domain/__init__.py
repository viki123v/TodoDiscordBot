from peewee import PostgresqlDatabase
from dotenv import load_dotenv
import os

load_dotenv()

user=os.getenv("POSTGRES_USER")
db=os.getenv("POSTGRES_DB")
password =os.getenv("POSTGRES_PASSWORD")
port=os.getenv("DB_PORT")

if user is None or db is None or password is None or port is None:
    raise ValueError("Missing database connection parameters")

db_con=PostgresqlDatabase(db,user=user,
                       password=password,
                       host='localhost',
                       port=port,
                       )

db_con.connect()