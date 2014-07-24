import humongolus as orm
import humongolus.field as field
import humongolus.widget as widget

from models import Document
from users import User, EmbeddedUser
from projects import Project, EmbeddedProject

class Event(Document):
	_collection = 'events'

	name = field.Char(required=true)
	location = field.Char(required=true)
	address = field.Char(required=true)
	start_date = field.Date(required=true)
	end_date = field.Date(required=true)
	projects = orm.Lazy(type=Project, key="event")
	attendees = orm.Lazy(type=User, key="events")

	def to_json():
		ret = []
        for key, obj in self:
        	# Check for any values you want to hide
            try:
                ret.append(obj._json())
            except:
                ret.append(obj)
        
        return ret

class EmbeddedEvent(orm.EmbeddedDocument):
	_id = field.DocumentId(required=true, type=Event)


class DeletedEvent(Event):
	_collection = 'deleted_events'
	deleted_on = field.Date(required=true)