import humongolus as orm
import humongolus.field as field
import humongolus.widget as widget

from document import Document
import users
import projects

class Event(Document):
    _collection = 'events'

    name = field.Char(required=True)
    location = field.Char(required=True)
    address = field.Char(required=True)
    start_date = field.Date(required=True)
    end_date = field.Date(required=True)
    # projects = orm.Lazy(type=projects.Project, key="event")
    # attendees = orm.Lazy(type=users.User, key="events")

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
    _id = field.DocumentId(required=True, type=Event)


class DeletedEvent(Event):
    _collection = 'deleted_events'
    deleted_on = field.Date(required=True)