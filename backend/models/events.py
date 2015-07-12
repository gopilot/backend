import mongoengine as orm
from bson.objectid import ObjectId
from . import document

class ScheduleItem(document.EmbeddedDocument):
    title = orm.StringField(required=True)
    location = orm.StringField()
    time = orm.DateTimeField(required=True)

class Event(document.Document):
    meta = {
        'allow_inheritance': True
    }
    name = orm.StringField(required=True)
    city = orm.StringField(required=True)
    slug = orm.StringField(required=True, unique=True)
    location = orm.StringField(required=True)
    address = orm.StringField(required=True)
    image = orm.URLField()

    start_date = orm.DateTimeField(required=True)
    end_date = orm.DateTimeField(required=True)
    registration_end = orm.DateTimeField(required=True)

    price = orm.IntField(default=0)

    schedule = orm.SortedListField(orm.EmbeddedDocumentField(ScheduleItem), ordering='time')
    
    @classmethod
    def find_event(cls, id):
        try:
            oid = ObjectId(id)
        except:
            return Event.objects(slug=id).first()

        return Event.objects(id=oid).first()
