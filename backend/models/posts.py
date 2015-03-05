import mongoengine as orm

from . import document, users, events

class Post(document.Document):
    event = orm.ReferenceField(events.Event, required=True)
    author = orm.ReferenceField(users.Organizer, required=True)
    time = orm.DateTimeField(required=True)

    title = orm.StringField(required=True)
    notif = orm.StringField() ## For SMS notifications
    
    image = orm.URLField()
    body = orm.StringField()