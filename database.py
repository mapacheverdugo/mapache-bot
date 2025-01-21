import os

from dotenv import load_dotenv
from peewee import *

load_dotenv()

db = SqliteDatabase(os.getenv('DB_PATH'))

def init_db():
    global db
    db = SqliteDatabase(os.getenv('DB_PATH'))
