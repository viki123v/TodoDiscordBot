from peewee import PostgresqlDatabase
from dotenv import load_dotenv
import os
import sys

load_dotenv()

user = os.getenv("POSTGRES_USER")
db = os.getenv("POSTGRES_DB")
password = os.getenv("POSTGRES_PASSWORD")

if user is None or db is None or password is None:
    raise ValueError("Missing database connection parameters")

profile=sys.argv[1]

port=None
host=None

if profile is None or not profile.strip() :
    raise ValueError('No profile provided')

profile=profile.strip()
if  profile == 'prod':
    port=5432
    host='db-prod'
elif profile == 'dev':
    port = os.getenv("DB_PORT")
    host = "localhost"

db_con = PostgresqlDatabase(db,
                            user=user,
                            password=password,
                            host=host,
                            port=port,
                            )

db_con.connect()
