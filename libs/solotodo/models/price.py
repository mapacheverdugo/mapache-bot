

import datetime

from peewee import *

from database import *


class Price(Model):
    normal_price = FloatField()
    offer_price = FloatField()
    store_name = CharField()
    store_url = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        database = db