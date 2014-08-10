from flask import Flask, Blueprint, request
import app

from dateutil import parser as dateParser
from datetime import datetime
import json
from bson import json_util
from bson.objectid import ObjectId
from app.models.users import User, Student, Mentor, Organizer
from app.models.events import Event, DeletedEvent

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

    event_id = event.save()

    if not event_id:
        return "Error creating event", 500

    user.managed_events.append( ObjectId(event_id) )

    return event.to_json()

# GET /events
@events.route('', methods=['GET'])
def all_events():
    events = []
    for evt in Event.find():
        events.append( evt.to_json_obj() )
    return json.dumps( events, default=json_util.default )

# GET /events/<event_id>
@events.route('/<event_id>', methods=['GET'])
def find_event(event_id):
    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    return event.to_json()

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

    deleted_event = DeletedEvent( id=event._id, from_collection="events" )
    deleted_event.deleted_on = datetime.today()
    deleted_event.save()

    event.remove()
    
    return 'Event deleted'


