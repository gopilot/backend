import mongoengine as orm

from . import document, events

class User(document.Document):
    meta = {
        'allow_inheritance': True
    }
    _hidden = ['password']
    type = orm.StringField()
    name = orm.StringField(required=True)
    image = orm.URLField()
    email = orm.EmailField(required=True)
    password = orm.StringField()
    complete = orm.BooleanField(default=True)
    completion_token = orm.StringField()
    # Different based on context of user - whether events attended, mentored, or organized
    events = orm.ListField( orm.ReferenceField(events.Event) )

    stripe_id = orm.StringField()

class Student(User):
   type = orm.StringField(default="student")

class Mentor(User):
    type = orm.StringField(default="mentor")

class Organizer(User):
    type = orm.StringField(default="organizer")

class DeletedUser(User):
    deleted_on = orm.DateTimeField(required=True)
