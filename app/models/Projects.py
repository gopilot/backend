import humongolus as orm
import humongolus.field as field
import humongolus.widget as widget
from bson.objectid import ObjectId
from document import Document
import users
import events

class Project(Document):
    _collection = 'projects'

    name = field.Char(required=True)
    event = field.DocumentId(type=events.Event)
    creators = orm.List(type=ObjectId)