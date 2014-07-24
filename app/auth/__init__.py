from flask import Flask, Blueprint, request, redirect, session
import app
import pymongo
from bson.objectid import ObjectId
from json import dumps
from uuid import uuid4 as random_uuid
import bcrypt

from models.users import User

auth = Blueprint('auth', __name__)

# Can be used to ensure that user is logged in. Returns the user_id if the user is logged in, otherwise returns False
def check_token(token):
	# TODO: Make this work
	if not token:
		return False

	user_id = app.sessions.get('session:'+token)
	if not user_id:
		return False
	
	return user_id

def create_token(user_id):
	token = random_uuid().hex
	app.sessions.set('session:'+token, user_id)
	return token;

@auth.route('/login', methods=["POST"])
def login():
	form_email = request.get_json().get('email')
	form_password = request.get_json().get('password').encode('utf-8')

	user = User.find_one({ 'email': form_email })
	if not user:
		return 'Email not found', 404

	hashed = user.password.encode('utf-8')

	if bcrypt.hashpw(form_password, hashed) == hashed:
		return {
			'session': create_token(user['_id']),
			'user': user.to_json()
		})
	else:
		return 'Incorrect password', 401

@auth.route('/signup', methods=["POST"])
def signup():
	form_name = request.json['name']
	form_email = request.json['email']
	form_password = request.json['password']
	form_type = request.json['type'] # student or mentor

	if User.find_one({'email': form_email }):
		return 'Email already exists', 400

	user = User()

	if form_type == 'student':
		user = Student()
	elif form_type == 'mentor':
		user = Mentor()
	elif form_type == 'organizer':
		user = Organizer()

	user.type = form_type
	user.name = form_name
	user.email = form_email
	user.password = bcrypt.hashpw( form_password.encode('utf-8'), bcrypt.gensalt() )

	user_id = user.save()

	if not insert_id:
		return 'Error creating account', 500
	
	return create_token(insert_id)


@auth.route('/check_session', methods=["GET"])
def check_session():
	token = request.args.get('session')
	if app.sessions.get('session:'+token):
		return "true"
	else:
		return "false"

@auth.route('/retrieve_user', methods=["GET"])
def retrieve_user():
	token = request.args.get('session')

	user_id = app.sessions.get('session:'+token)
	if not user_id:
		return "Session invalid", 401

	user = User.find_one({'_id': user_id })

	if not user:
		return "Session invalid", 401

	return user.to_json()



	