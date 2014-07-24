from flask import Flask, Blueprint, request
import app

from dateutil import parser as dateParser
from datetime import datetime

from models.users import User
from models.events import Event, EmbeddedEvent, DeletedEvent

events = Blueprint('events', __name__)



# POST /events
@events.route('', methods=['POST'])
def create_event():
	user_id = app.auth.check_token( request.args.get('session') )

	if not user_id:
		return "Unauthorized request: Bad session token", 401

	user = User.find_one({'_id': user_id })

	if not user or not user.type == 'organizer':
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

	user.managed_events.append( EmbeddedEvent(_id=event_id) )

	return str(event_id)

# GET /events/<event_id>
@events.route('/<event_id>', methods=['GET'])
def find_event(event_id):
	## Do we need auth here?
	event = Event.find_one({'_id': event_id })
	if not event:
		return "Event not found", 404

	return event.to_json()

# PUT /events/<event_id>
@events.route('/<event_id>', methods=['PUT'])
def update_event(event_id):
	user_id = app.auth.check_token( request.args.get('session') )
	if not user_id:
		return "Unauthorized request: Bad session token", 401

	user = User.find_one({'_id': user_id })
	if not user.type == 'organizer':
		return "Unauthorized request: User doesn't have permission", 401

	event = Event.find_one({'_id': event_id })
	if not event:
		return "Event not found", 404


	for key, value in request.get_json().items():
		if not key.startswith('_'):
			event.setattr(key, value)

	event.save()

	return event.to_json()

# DELETE /events/<event_id>
@events.route('/<event_id>', methods=["DELETE"])
def remove_event(event_id):
	user_id = app.auth.check_token( request.args.get('session') )
	if not user_id:
		return "Unauthorized request: Bad session token", 401

	user = Event.find_one({'_id': user_id })
	if not user.type == 'organizer':
		return "Unauthorized request: User doesn't have permission", 401

	event = Event.find_one({'_id': event_id })
	if not event:
		return "Event not found", 404

	deleted_event = DeletedEvent(base=event)
	deleted_event.deleted_on = datetime.today()
	deleted_event.save()

	event.remove()
	
	return 'Event deleted'


