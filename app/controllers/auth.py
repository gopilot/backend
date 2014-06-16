from flask import Flask, render_template, request, redirect, make_response, session
from app import app, db

import pymongo
from bson import objectid
import bcrypt

# Can be used to ensure that user is logged in. Returns the user if the user is logged in, otherwise returns False
def ensure_login():
	if 'user_id' in session:
		print 'cookie exists'
		cookie = session['user_id']
	else:
		return False

	user = db.users.find_one({ '_id': objectid.ObjectId(cookie) });
	if user:
		return user
	else:
		print 'no user', cookie
		return False

# POST /login
def login():
	form_email = request.form.get('email')
	form_password = request.form.get('password').encode('utf-8')

	user = db.users.find_one({ 'email': form_email })
	if not user:
		response.status = 'Email not found'
		return 'Email not found', 404

	hashed = user['password'].encode('utf-8')

	if bcrypt.hashpw(form_password, hashed)==hashed:
		session['user_id'] = str(user['_id'])
		return redirect('/')
	else:
		return 'Incorrect password', 401

# POST /signup
def signup():
	form_name = request.form.get('name')
	form_email = request.form.get('email')
	form_password = request.form.get('password')
	form_type = request.form.get('type') # student or mentor

	insert_id = db.users.save({
		'name': form_name,
		'email': form_email,
		'password': bcrypt.hashpw( form_password.encode('utf-8'), bcrypt.gensalt() ),
		'type': form_type
	});

	if not insert_id:
		return 'Error creating account', 500
	else:
		session['user_id'] = str(insert_id)
		return redirect('/')

# GET /logout
def logout():
	if 'user_id' in session:
		del session['user_id']

	return redirect('/')





	