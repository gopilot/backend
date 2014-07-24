import humongolus as orm
import humongolus.field as field
import humongolus.widget as widget

from models import Document
from users import User, EmbeddedUser
from events import Event, EmbeddedEvent

class Project(Document):
	_collection = 'projects'

	name = field.Char(required=true)
	event = field.DocumentId(type=Event)
	owners = field.List(type=EmbeddedUser) # Better way to do this? We want an array of DocumentIds

class EmbeddedProject(orm.EmbeddedDocument)
	_id = field.DocumentId(required=true, type=Project)