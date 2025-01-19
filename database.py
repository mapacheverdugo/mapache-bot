from peewee import *

db = SqliteDatabase('mapache_bot.db')

def init_db():
    global db
    db = SqliteDatabase('mapache_bot.db')
