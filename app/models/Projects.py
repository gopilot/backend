import humongolus as orm
import humongolus.field as field
import humongolus.widget as widget

from document import Document
import users
import events

class Project(Document):
    _collection = 'projects'

    name = field.Char(required=True)
    # event = field.DocumentId(type=events.Event)
    # owners = field.List(type=users.EmbeddedUser) # Better way to do this? We want an array of DocumentIds

class EmbeddedProject(orm.EmbeddedDocument):
    _id = field.DocumentId(required=True, type=Project)