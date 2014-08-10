from flask import Flask, Blueprint, request
import app

from dateutil import parser as dateParser
from datetime import datetime
import json
from bson import json_util
from app.models.users import User, Student, Mentor, Organizer
from app.models.events import Event, DeletedEvent

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

    event.organizers.append( user )

    event.save()

    if not event.id:
        return "Error creating event", 500

    return event.to_json()

# GET /events
@events.route('', methods=['GET'])
def all_events():
    events = []
    for evt in Event.objects:
        events.append( evt.to_json_obj() )

    return json.dumps( events, default=json_util.default ), 200, jsonType

# GET /events/<event_id>
@events.route('/<event_id>', methods=['GET'])
def find_event(event):
    
    if not event:
        return "Event not found", 404

    return event.to_json()

# PUT /events/<event_id>
@events.route('/<event_id>', methods=['PUT'])
def update_event(event):
    user_id = app.auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    if not event:
        return "Event not found", 404


    for key, value in request.get_json().items():
        if not key.startswith('_'): # Some security
            setattr(event, key, value)

    event.save()

    return event.to_json()

# DELETE /events/<event_id>
@events.route('/<event_id>', methods=["DELETE"])
def remove_event(event):
    user_id = app.auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    if not event:
        return "Event not found", 404

    deleted_event = DeletedEvent(event.id)
    deleted_event.deleted_on = datetime.today()
    deleted_event.save()

    event.remove()
    
    return 'Event deleted'


