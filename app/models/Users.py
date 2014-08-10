import humongolus as orm
import humongolus.field as field
import humongolus.widget as widget
from bson.objectid import ObjectId
from document import Document
import events
from app import db

class User(Document):
    _collection = 'users'
    _indexes = [
        orm.Index("email", key=[('email', orm.Index.DESCENDING)])
    ]
    _hidden = ['password']

    type = field.Char(required=True)
    name = field.Char(required=True)
    image = field.Url()
    email = field.Email(required=True)
    password = field.Char(required=True)
    events = orm.List(type=ObjectId)

class Student(User):
    type = field.Char(required=True, default='student')

    @classmethod
    def find_one(cls, *args, **kwargs):
        if isinstance(args[0], dict):
            args[0]['type'] = 'student';

        res = db.users.find_one(args[0])
        if(res):
            return Student( cls._connection().find_one(*args, **kwargs) );
        else:
            return None

class Mentor(User):
    type = field.Char(required=True, default='mentor')

    @classmethod
    def find_one(cls, *args, **kwargs):
        if isinstance(args[0], dict):
            args[0]['type'] = 'mentor';

        res = db.users.find_one(args[0])
        if(res):
            return Mentor( cls._connection().find_one(*args, **kwargs) );
        else:
            return None

class Organizer(User):
    type = field.Char(required=True, default='organizer')
    managed_events = orm.List(type=ObjectId)

    @classmethod
    def find_one(cls, *args, **kwargs):
        if isinstance(args[0], dict):
            args[0]['type'] = 'organizer';

        res = db.users.find_one(args[0])
        if(res):
            return Organizer( cls._connection().find_one(*args, **kwargs) );
        else:
            return None

class DeletedUser(User):
    _collection = 'deleted_events'
    deleted_on = field.Date(required=True)
