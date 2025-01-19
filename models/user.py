
import datetime

from peewee import *

from database import *


class User(Model):
    user_id = IntegerField()
    current_step = IntegerField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


