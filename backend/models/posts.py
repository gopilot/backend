import mongoengine as orm

from . import document, users, events

class Post(document.Document):
    event = orm.ReferenceField(events.Event)
    author = orm.ReferenceField(users.Organizer)
    time = orm.DateTimeField(required=True)

    title = orm.StringField(required=True)
    notif = orm.StringField(required=True) ## For push notifications
    
    image = orm.URLField()
    body = orm.StringField()