import mongoengine as orm

from . import document, users, events

class Project(document.Document):
    name = orm.StringField()
    image = orm.URLField()
    description = orm.StringField()
    event = orm.ReferenceField(events.Event)
    team = orm.ListField( orm.ReferenceField(users.Student), default=[] )
    prize = orm.StringField()