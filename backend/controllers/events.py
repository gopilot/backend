from flask import Flask, request

from dateutil import parser as dateParser
from datetime import datetime

from backend import EventBlueprint, app
from . import auth

from backend.models import User, Student, Mentor, Organizer, Event

import json
from twitter import *

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
    event.city = body.get('city')
    event.slug = body.get('slug')

    if body.get('price'):
        event.price = int(body.get('price'))

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
    event = Event.find_event( event_id )
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

    event = Event.find_event( event_id )
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

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    event.delete()
    
    return 'Event deleted'

# GET /events/<event_id>/tweets
@EventBlueprint.route('/<event_id>/tweets', methods=['GET'])
def find_tweets(event_id):
    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    twitter = Twitter(auth=OAuth2(bearer_token=app.config['TWITTER_TOKEN']))

    data = []
    for tweet in twitter.search.tweets(q='#'+event.name, result_type="recent"):
        data.append({
            'time': tweet.created_at,
            'text': tweet.text,
            'user': tweet.user.screen_name
        })

    return data