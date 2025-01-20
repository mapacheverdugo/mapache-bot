

import datetime

from peewee import *

from database import *
from libs.solotodo.models.product import Product


class Price(Model):
    solotodo_id = BigIntegerField(index=True)
    normal_price = FloatField()
    offer_price = FloatField()
    store_solotodo_id = IntegerField()
    external_url = CharField()
    product = ForeignKeyField(Product, backref='prices')
    timestamp = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        database = db