from peewee import *

from database import *


class Store(Model):
    solotodo_id = IntegerField()
    name = CharField()
    logo_url = CharField()
    
    class Meta:
        database = db