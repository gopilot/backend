from flask import Flask, Blueprint, request
import app

from dateutil import parser as dateParser
from datetime import datetime

from app.models.users import User, Student, Mentor, Organizer
from app.models.events import Event, DeletedEvent

import json

from . import events, jsonType
print 'registration'

## These endpoints need any security?
@events.route('/<event_id>/<attendee_type>', methods=['GET'])
def get_attendees(event_id, attendee_type):
    if not event_id:
        return "Event ID required", 400
    if not Event.find_id( event_id ):
        return "Event not found", 404

    attendee_type = attendee_type.lower()
    if attendee_type not in ['attendees', 'students', 'mentors', 'organizers']:
        return "Invalid Attendee Type", 404

    attendees = None
    if attendee_type == 'attendees':
        attendees = {
            'students': [],
            'mentors': [],
            'organizers': []
        }
        
        for usr in User.objects(events=event_id):
            if usr.type in ['student', 'mentor', 'organizer']:
                attendees[ usr.type+'s' ].append( usr.to_dict() )
            else:
                if not attendees['other']:
                    attendees['other'] = []
                attendees['other'].append( usr.to_dict() )
    else:
        attendees = []
        attendee_cls = None
        if attendee_type == 'students':
            attendee_cls = Student
        elif attendee_type == 'mentors':
            attendee_cls = Mentor
        elif attendee_type == 'organizers':
            attendee_cls = Organizer
        else:
            attendee_cls = User

        
        for usr in attendee_cls.objects(events=event_id):
            attendees.append( usr.to_dict() )

    return json.dumps( attendees ), 200, jsonType

@events.route('/<event_id>/register', methods=['POST'])
def register(event_id):
    user_id = app.auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = User.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    user.events.append( event_id )
    user.save()

    if user.type == 'student' or user.type == 'mentor':
        ## Send confirmation email
        pass;

    return "OK", 200

@events.route('/<event_id>/register', methods=['DELETE'])
def unregister(event_id):
    user_id = app.auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = User.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    user.events.remove( event_id )
    user.save()

    return "OK", 200


