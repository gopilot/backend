import humongolus as orm
import humongolus.field as field
import humongolus.widget as widget

from Users import User, EmbeddedUser
from Projects import Project, EmbeddedProject

class Event(orm.Document):
	_db = 'backend'
	_collection = 'events'

	name = field.Char(required=true)
	location = field.Char(required=true)
	address = field.Char(required=true)
	start_date = field.Date(required=true)
	end_date = field.Date(required=true)
	projects = orm.Lazy(type=project, key="event")

class EmbeddedEvent(orm.EmbeddedDocument):
	_id = field.DocumentId(required=true, type=Event)