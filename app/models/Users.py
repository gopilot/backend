import humongolus as orm
import humongolus.field as field
import humongolus.widget as widget

from models import Document
from events import Event, EmbeddedEvent
from projects import Project, EmbeddedProject

class User(Document):
	_collection = 'users'
	_indexes = [
		orm.Index("email", key=[('email', orm.Index.DESCENDING)])
	]

	type = field.Char(required=true)
	name = field.Char(required=true)
	image = field.Url()
	email = field.Email(required=true)
	password = field.Char(required=true)
	events = orm.List(type=EmbeddedEvent) # Better way to do this? We want an array of DocumentIds


class EmbeddedUser(orm.EmbeddedDocument):
	_id = field.DocumentId(required=true, type=User)


class Student(User):
	type = field.Char(required=true, default='student')

class Mentor(User):
	type = field.Char(required=true, default='mentor')

class Organizer(User):
	type = field.Char(required=true, default='organizer')