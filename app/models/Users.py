import humongolus as orm
import humongolus.field as field
import humongolus.widget as widget

from document import Document
import events
import projects

class User(Document):
    _collection = 'users'
    _indexes = [
        orm.Index("email", key=[('email', orm.Index.DESCENDING)])
    ]
    _hidden = ['password']

    type = field.Char(required=True)
    name = field.Char(required=True)
    image = field.Url()
    email = field.Email(required=True)
    password = field.Char(required=True)
    events = orm.List(type=events.EmbeddedEvent) # Better way to do this? We want an array of DocumentIds


class EmbeddedUser(orm.EmbeddedDocument):
    _id = field.DocumentId(required=True, type=User)


# TODO: Find a way we can call User.find and User.find_one and still get Students or Mentors

class Student(User):
    type = field.Char(required=True, default='student')

class Mentor(User):
    type = field.Char(required=True, default='mentor')

class Organizer(User):
    type = field.Char(required=True, default='organizer')