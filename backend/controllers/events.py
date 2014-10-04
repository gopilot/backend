from flask import Flask, request

from dateutil import parser as dateParser
from datetime import datetime

from backend import EventBlueprint
from . import auth

from backend.models.users import User, Student, Mentor, Organizer
from backend.models.events import Event, DeletedEvent

import json

jsonType = {'Content-Type': 'application/json'}


# POST /events
@EventBlueprint.route('', methods=['POST'])
def create_event():
    user_id = auth.check_token( request.headers.get('session') )

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
    event.registration_end = dateParser.parse( body.get('registration_end') )
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
@EventBlueprint.route('', methods=['GET'])
def all_events():
    events = []
    for evt in Event.objects:
        events.append( evt.to_dict() )

    return json.dumps( events ), 200, jsonType

# GET /events/<event_id>
@EventBlueprint.route('/<event_id>', methods=['GET'])
def find_event(event_id):
    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    return event.to_json()

# PUT /events/<event_id>
@EventBlueprint.route('/<event_id>', methods=['PUT'])
def update_event(event_id):
    user_id = auth.check_token( request.headers.get('session') )
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
@EventBlueprint.route('/<event_id>', methods=["DELETE"])
def remove_event(event_id):
    user_id = auth.check_token( request.headers.get('session') )
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