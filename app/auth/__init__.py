from flask import Flask, Blueprint, request, redirect, session
from app import app, db

import pymongo
from bson import objectid
from uuid import uuid4 as random_uuid

auth = Blueprint('auth', __name__)

# Can be used to ensure that user is logged in. Returns the user if the user is logged in, otherwise returns False
def ensure_login():
	# TODO: Make this work

	user = db.users.find_one({ '_id': objectid.ObjectId(cookie) });
	if user:
		return user
	else:
		print 'no user', cookie
		return False

def create_token(user_id):
	token = random_uuid().hex
	db.users.update({ '_id': user_id }, { '$push': { 'tokens': token } } );
	return token;

@auth.route('/login', methods=["POST"])
def login():
	form_email = request.form.get('email')
	form_password = request.form.get('password').encode('utf-8')

	user = db.users.find_one({ 'email': form_email })
	if not user:
		response.status = 'Email not found'
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

@auth.route('/logout', methods=["GET"])
def logout():
	if 'user_id' in session:
		del session['user_id']

	return redirect('/')





	