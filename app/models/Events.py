import humongolus as orm
import humongolus.field as field
import humongolus.widget as widget

from document import Document

class Event(Document):
    _collection = 'events'

    name = field.Char(required=True)
    location = field.Char(required=True)
    address = field.Char(required=True)
    image = field.Url()
    start_date = field.Date(required=True)
    end_date = field.Date(required=True)


class DeletedEvent(Event):
    _collection = 'deleted_events'
    deleted_on = field.Date(required=True)
