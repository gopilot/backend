from flask import Flask, Blueprint, request, redirect, session
from app import app, db, sessions

import pymongo
from bson import objectid
from uuid import uuid4 as random_uuid
import bcrypt

auth = Blueprint('auth', __name__)

# Can be used to ensure that user is logged in. Returns the user_id if the user is logged in, otherwise returns False
def check_token(token):
	# TODO: Make this work
	user_id = session.get('session:'+token)
	if user_id:
		return user_id
	else:
		print 'no user', user_id
		return False

def create_token(user_id):
	token = random_uuid().hex
	sessions.set('session:'+token, user_id)
	return token;

@auth.route('/login', methods=["POST"])
def login():
	form_email = request.form.get('email')
	form_password = request.form.get('password').encode('utf-8')

	user = db.users.find_one({ 'email': form_email })
	if not user:
		return 'Email not found', 404

	hashed = user['password'].encode('utf-8')

	if bcrypt.hashpw(form_password, hashed)==hashed:
		return create_token(user['_id'])
	else:
		return 'Incorrect password', 401

@auth.route('/signup', methods=["POST"])
def signup():
	form_name = request.form.get('name')
	form_email = request.form.get('email')
	form_password = request.form.get('password')
	form_type = request.form.get('type') # student or mentor

	insert_id = db.users.insert({
		'name': form_name,
		'email': form_email,
		'password': bcrypt.hashpw( form_password.encode('utf-8'), bcrypt.gensalt() ),
		'type': form_type
	});

	if not insert_id:
		return 'Error creating account', 500
	else:
		return create_token(insert_id)

@auth.route('/debug_token', methods=["GET"])
def debug_token():
	token = request.args.get('token')
	if sessions.get('session:'+token):
		return "Valid token"
	else:
		return "Invalid token"


	