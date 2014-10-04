import mongoengine as orm

from . import document, users, events

class Post(document.Document):
    event = orm.ReferenceField(events.Event)
    author = orm.ReferenceField(users.Organizer)

    title = orm.StringField(required=True)
    notif = orm.StringField(required=True) ## For push notifications
    image = orm.StringField()

    body = orm.StringField(required=True)