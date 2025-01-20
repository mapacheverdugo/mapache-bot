

import datetime

from peewee import *

from database import *
from libs.solotodo.models.price import Price
from libs.solotodo.models.product import Product
from models.user import User


class ProductSubscription(Model):
    custom_name = CharField()
    user = ForeignKeyField(User, backref='subscriptions')
    product = ForeignKeyField(Product, backref='subscriptions')
    poll_interval = IntegerField(default=60)
    first_seen_offer_lower_price = ForeignKeyField(Price, null=True)
    first_seen_normal_lower_price = ForeignKeyField(Price, null=True)
    latest_seen_offer_lower_price = ForeignKeyField(Price, null=True)
    latest_seen_normal_lower_price = ForeignKeyField(Price, null=True)
    last_seen_available = BooleanField(default=True)
    historical_variation_until_notify = FloatField(default=0.2)
    latest_seen_variation_from_notify = FloatField(default=0)
    notify_when_unavailable = BooleanField(default=True)
    notify_when_available = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db