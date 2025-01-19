

import datetime

from peewee import *

from database import *
from libs.solotodo.models.product import Product
from models.user import User


class ProductSubscription(Model):
    custom_name = CharField()
    user = ForeignKeyField(User, backref='subscriptions')
    product = ForeignKeyField(Product, backref='subscriptions')
    poll_interval = IntegerField()
    url = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)
    saved = BooleanField(default=False)

    class Meta:
        database = db