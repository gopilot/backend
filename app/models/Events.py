import mongoengine as orm

from document import Document

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
    registration_end = orm.DateTimeField(required=True)

class DeletedEvent(Event):
    deleted_on = orm.DateTimeField(required=True)
