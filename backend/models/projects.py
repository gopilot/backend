import mongoengine as orm

from . import document, users, events

class Project(document.Document):
    name = orm.StringField(required=True)
    event = orm.ReferenceField(events.Event)
    creators = orm.ListField( orm.ReferenceField(users.Student), default=[] )
    description = orm.StringField()
    link_github = orm.StringField()
    link_view = orm.StringField()
    link_use = orm.StringField()