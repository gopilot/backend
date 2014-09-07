import mongoengine as orm

from document import Document
import events

class User(Document):
    meta = {
        'allow_inheritance': True
    }
    _hidden = ['password']
    type = orm.StringField()
    name = orm.StringField(required=True)
    image = orm.URLField()
    email = orm.EmailField(required=True)
    password = orm.StringField(required=True)

    # Different based on context of user - whether events attended, mentored, or organized
    events = orm.ListField( orm.ReferenceField(events.Event) )

class Student(User):
   type = orm.StringField(default="student")

class Mentor(User):
    type = orm.StringField(default="mentor")

class Organizer(User):
    type = orm.StringField(default="organizer")

class DeletedUser(User):
    deleted_on = orm.DateTimeField(required=True)
