from flask import Flask, Blueprint, request
from app import app, db, auth
from dateutil import parser as dateParser
from datetime import datetime
from bson.json_util import dumps as to_json
from bson.objectid import ObjectId
events = Blueprint('events', __name__)

@events.route('/', methods=['POST'])
def create_event():
	user_id = auth.check_token( request.args.get('session') )
	print 'user2', user_id
	if not user_id:
		return "Unauthorized request: Bad session token", 401

	user = db.users.find_one({'_id': ObjectId(user_id) })
	print 'user', user
	if not user or not user['type'] == 'organizer':
		return "Unauthorized request: User doesn't have permission", 401

	body = request.get_json()
	event_name = body.get('name')
	event_start_date = dateParser.parse( body.get('start_date') )
	event_end_date = dateParser.parse( body.get('end_date') )
	event_location = body.get('location')
	event_address = body.get('address')

	event_id = db.events.insert({
		'name': event_name,
		'start_date': event_start_date,
		'end_date': event_end_date,
		'location': event_location,
		'address': event_address
	})

	if not event_id:
		return "Error creating event", 500

	db.users.update(user, { '$push': {'events': event_id} })

	return str(event_id)

@events.route('/<event_id>', methods=['GET'])
def find_event(event_id):
	## Do we need auth here?
	event = db.events.find_one({'_id': ObjectId(event_id) })
	if not event:
		return "Event not found", 404

	return to_json(event)

@events.route('/<event_id>', methods=['PUT'])
def update_event(event_id):
	user_id = auth.check_token( request.args.get('session') )
	if not user_id:
		return "Unauthorized request: Bad session token", 401

	user = db.users.find_one({'_id': ObjectId(user_id) })
	if not user['type'] == 'organizer':
		return "Unauthorized request: User doesn't have permission", 401

	event = db.events.find_one({'_id': ObjectId(event_id) })
	if not event:
		return "Event not found", 404


	for key, value in request.get_json().items():
		event[key] = value

	db.events.save(event)

	return to_json(event)

@events.route('/<event_id>', methods=["DELETE"])
def remove_event(event_id):
	user_id = auth.check_token( request.args.get('session') )
	if not user_id:
		return "Unauthorized request: Bad session token", 401

	user = db.users.find_one({'_id': ObjectId(user_id) })
	if not user['type'] == 'organizer':
		return "Unauthorized request: User doesn't have permission", 401

	event = db.events.find_one({'_id': ObjectId(event_id) })
	if not event:
		return "Event not found", 404

	db.events.remove(event)
	event['deleted_on'] = datetime.today()
	db.deleted_events.insert(event)
	
	return 'Event Deleted'


