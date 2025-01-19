
from peewee import *

from database import *
from libs.solotodo.models.price import Price


class Product(Model):
    solotodo_id = IntegerField()
    name = CharField()
    url = CharField()
    current_offer_lower_price = ForeignKeyField(Price, backref='product')
    current_normal_lower_price = ForeignKeyField(Price, backref='product')

    class Meta:
        database = db