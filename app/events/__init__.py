from flask import Flask, Blueprint, request
import app

from dateutil import parser as dateParser
from datetime import datetime

from app.models.users import User, Student, Mentor, Organizer
from app.models.events import Event, DeletedEvent

import json

jsonType = {'Content-Type': 'application/json'}

events = Blueprint('events', __name__)

# POST /events
@events.route('', methods=['POST'])
def create_event():
    user_id = app.auth.check_token( request.headers.get('session') )

    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )

    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    body = request.get_json()
    event = Event()
    event.name = body.get('name')
    event.start_date = dateParser.parse( body.get('start_date') )
    event.end_date = dateParser.parse( body.get('end_date') )
    event.location = body.get('location')
    event.address = body.get('address')
    event.image = body.get('image')

    event.save()

    user.events.append( event )

    user.save()

    if not event.id:
        return "Error creating event", 500

    return event.to_json()

# GET /events
@events.route('', methods=['GET'])
def all_events():
    events = []
    for evt in Event.objects:
        events.append( evt.to_dict() )

    return json.dumps( events ), 200, jsonType

# GET /events/<event_id>
@events.route('/<event_id>', methods=['GET'])
def find_event(event_id):
    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    return event.to_json()

## These endpoints need any security?
@events.route('/<event_id>/attendees', methods=['GET'])
def get_attendees(event_id):
    attendees = dict(
        students=[],
        mentors=[],
        organizers=[]
    )
    
    for usr in User.objects(events=event_id):
        if usr.type in ['student', 'mentor', 'organizer']:
            attendees[ usr.type+'s' ].append( usr.to_dict() )
        else:
            attendees['other'].append( usr.to_dict() )

    return json.dumps( attendees ), 200, jsonType

@events.route('/<event_id>/students', methods=['GET'])
def get_students(event_id):
    students = []
    for usr in Student.objects(events=event_id):
        students.append( usr.to_dict() )
    return json.dumps( students ), 200, jsonType

@events.route('/<event_id>/mentors', methods=['GET'])
def get_mentors(event_id):
    mentors = []
    for usr in Mentor.objects(events=event_id):
        mentors.append( usr.to_dict() )
    return json.dumps( mentors )

@events.route('/<event_id>/organizers', methods=['GET'])
def get_organizers(event_id):
    organizers = []
    for usr in Organizer.objects(events=event_id):
        organizers.append( usr.to_dict() )
    return json.dumps( organizers )

# PUT /events/<event_id>
@events.route('/<event_id>', methods=['PUT'])
def update_event(event_id):
    user_id = app.auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404


    for key, value in request.get_json().items():
        if not key.startswith('_'): # Some security
            setattr(event, key, value)

    event.save()

    return event.to_json()

# DELETE /events/<event_id>
@events.route('/<event_id>', methods=["DELETE"])
def remove_event(event_id):
    user_id = app.auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    deleted_event = DeletedEvent(**event._data)
    deleted_event.deleted_on = datetime.today()
    deleted_event.save()

    event.delete()
    
    return 'Event deleted'


