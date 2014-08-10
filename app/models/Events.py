import mongoengine as orm

from document import Document
import users

class Event(Document):
    meta = {
        'allow_inheritance': True
    }
    name = orm.StringField(required=True)
    location = orm.StringField(required=True)
    address = orm.StringField(required=True)
    image = orm.URLField()

    start_date = orm.DateTimeField(required=True)
    end_date = orm.DateTimeField(required=True)

    organizers = orm.ListField( orm.ReferenceField(users.Organizer) )
    attendees = orm.ListField( orm.ReferenceField(users.Student) )
    mentors = orm.ListField( orm.ReferenceField(users.Mentor) )

class DeletedEvent(Event):
    _collection = 'deleted_events'
    deleted_on = orm.DateTimeField(required=True)
