import mongoengine as orm

from document import Document
import users
import events

class Project(Document):
    name = orm.StringField(required=True)
    event = orm.ReferenceField(events.Event)
    creators = orm.ListField( orm.ReferenceField(users.Student), default=[] )