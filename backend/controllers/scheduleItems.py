from flask import Flask, request

from dateutil import parser as dateParser
from datetime import datetime

from backend import EventBlueprint
from . import auth

from backend.models import User, Student, Mentor, Organizer, Event, ScheduleItem

import json
jsonType = {'Content-Type': 'application/json'}

# POST /schedule
@EventBlueprint.route('/<event_id>/schedule', methods=['POST'])
def create_scheduleitem(event_id):
    user_id = auth.check_token( request.headers.get('session') )

    if not user_id:
        return "Unauthorized request: Bad session token", 401

    organizer = Organizer.find_id( user_id )
    if not organizer:
        return "Unauthorized request: User doesn't have permission", 401


    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    body = request.get_json()
    schedule = ScheduleItem(
        title=body.get('title'),
        location=body.get('location'),
        time = dateParser.parse( body.get('time') )
    )
    
    event.schedule.append(schedule)
    event.save()
    event.reload()

    return event.to_json()

# GET /schedule
@EventBlueprint.route('/<event_id>/schedule', methods=['GET'])
def all_scheduleitems(event_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = User.find_id( user_id )
    if not user:
        return "User not found", 404

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    attended_ids = [ evt.id for evt in user.events ]

    if not (event.id in attended_ids or user.type == "organizer"):
        return "Unauthorized request: User doesn't have permission"

    schedule = []
    for s in event.schedule:
        schedule.append(s.to_dict())

    return json.dumps( schedule ), 200, jsonType

# PUT /schedule/<index>
@EventBlueprint.route('/<event_id>/schedule/<index>', methods=['PUT'])
def update_scheduleitem(event_id, index):
    index = int(index)
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    if not (0 <= index < len(event.schedule)):
        return "Schedule Item not found", 404
    schedule = event.schedule[index]

    for key, value in request.get_json().items():
        if not key.startswith('_'): # Some security
            setattr(schedule, key, value)

    event.schedule[index] = schedule;

    return event.to_json()

# DELETE /schedule/<index>
@EventBlueprint.route('/<event_id>/schedule/<index>', methods=["DELETE"])
def delete_scheduleitem(event_id, index):
    index = int(index)
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    if not (0 <= index < len(event.schedule)):
        return "Schedule item not found", 404

    event.schedule.pop(index)
    
    return 'Schedule item deleted'