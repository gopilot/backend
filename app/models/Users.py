import mongoengine as orm

from document import Document

class User(Document):
    meta = {
        'allow_inheritance': True,
        'hidden': ['password']
    }
    _hidden = ['password']
    type = orm.StringField()
    name = orm.StringField(required=True)
    image = orm.URLField()
    email = orm.EmailField(required=True)
    password = orm.StringField(required=True)

class Student(User):
   type = "student"

class Mentor(User):
    type = "mentor"

class Organizer(User):
    type = "organizer"

class DeletedUser(User):
    deleted_on = orm.DateTimeField(required=True)
