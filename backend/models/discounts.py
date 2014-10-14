import mongoengine as orm

from . import document, users, events

class Discount(document.Document):
    event = orm.ReferenceField(events.Event)

    title = orm.StringField(required=True)
    amount = orm.IntField(required=True) ## For push notifications
    code = orm.StringField(required=True)

    active = orm.BooleanField(default=True)
    limit = orm.IntField()

    claimed = orm.ListField( orm.ReferenceField(users.User) )