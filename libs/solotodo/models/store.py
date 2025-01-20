from peewee import *

from database import *


class Store(Model):
    solotodo_id = IntegerField()
    name = CharField()
    logo_url = CharField()
    preferred_payment_method = CharField(null=True)
    
    class Meta:
        database = db