import mongoengine as orm

from . import document, events

class User(document.Document):
    meta = {
        'allow_inheritance': True
    }
    _hidden = ['password', 'completion_token']
    type = orm.StringField()

    name = orm.StringField(required=True)
    image = orm.URLField()
    email = orm.EmailField(required=True, unique=True)
    password = orm.StringField()

    gender = orm.StringField()
    phone = orm.StringField()

    complete = orm.BooleanField(default=True)
    completion_token = orm.StringField()

    # Different based on context of user - whether events attended, mentored, or organized
    checkins = orm.ListField( orm.ReferenceField(events.Event) )
    events = orm.ListField( orm.ReferenceField(events.Event) )

    shirt_type = orm.StringField()
    shirt_size = orm.StringField()

    dietary = orm.StringField()
    notes = orm.MapField( orm.StringField() )

    stripe_id = orm.StringField()

class Student(User):
    type = orm.StringField(default="student")

    grade = orm.StringField()
    school = orm.StringField()
    birth_date = orm.DateTimeField()
    emergency_name = orm.StringField()
    emergency_email = orm.EmailField()
    emergency_phone = orm.StringField()
    has_experience = orm.BooleanField()
    experience_years = orm.StringField()
     


class Mentor(User):
    type = orm.StringField(default="mentor")
    title = orm.StringField()
    company = orm.StringField()
    has_experience = orm.BooleanField()
    skills = orm.StringField()
    profiles = orm.StringField()


class Organizer(User):
    type = orm.StringField(default="organizer")
