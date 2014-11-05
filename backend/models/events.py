import mongoengine as orm

from . import document

class Event(document.Document):
    meta = {
        'allow_inheritance': True
    }
    name = orm.StringField(required=True)
    location = orm.StringField(required=True)
    address = orm.StringField(required=True)
    image = orm.URLField()

    start_date = orm.DateTimeField(required=True)
    end_date = orm.DateTimeField(required=True)
    registration_end = orm.DateTimeField(required=True)

    price = orm.IntField(default=0)

