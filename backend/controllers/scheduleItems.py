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
    schedule = ScheduleItem()

    schedule.title = body.get('title')
    schedule.location = body.get('location')
    schedule.time = dateParser.parse( body.get('time') )
    
    schedule.save()

    event.schedule.append(schedule)
    event.save()

    if not schedule.id:
        return "Error creating schedule item", 500

    return schedule.to_json()

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

# GET /schedule/<scheduleitem_id>
@EventBlueprint.route('/<event_id>/schedule/<scheduleitem_id>', methods=['GET'])
def get_scheduleitem(event_id, scheduleitem_id):
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

    schedule = ScheduleItem.find_id( scheduleitem_id )
    if not schedule:
        return "Schedule item not found", 404

    return schedule.to_json()

# PUT /schedule/<scheduleitem_id>
@EventBlueprint.route('/<event_id>/schedule/<scheduleitem_id>', methods=['PUT'])
def update_scheduleitem(event_id, scheduleitem_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    schedule = ScheduleItem.find_id( scheduleitem_id )
    if not schedule:
        return "Schedule Item not found", 404

    for key, value in request.get_json().items():
        if not key.startswith('_'): # Some security
            setattr(schedule, key, value)

    schedule.save()

    return schedule.to_json()

# DELETE /schedule/<scheduleitem_id>
@EventBlueprint.route('/<event_id>/schedule/<scheduleitem_id>', methods=["DELETE"])
def delete_scheduleitem(event_id, scheduleitem_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    schedule = ScheduleItem.find_id( scheduleitem_id )
    if not schedule:
        return "Schedule item not found", 404

    event.schedule.remove(schedule)
    schedule.delete()
    
    return 'Schedule item deleted'