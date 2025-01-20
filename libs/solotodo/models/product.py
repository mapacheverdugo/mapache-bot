
from peewee import *

from database import *


class Product(Model):
    solotodo_id = IntegerField()
    name = CharField()
    url = CharField()

    class Meta:
        database = db