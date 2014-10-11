from flask import Flask, request, render_template, json, Blueprint, make_response
import os
import sys
import pymongo
import redis
import mongoengine
from bson.objectid import ObjectId
import logging

from datetime import timedelta
from functools import update_wrapper

app = Flask(__name__)
app.debug = True

app.config['MONGO_URL'] 	= os.getenv('MONGO_URL',	'mongodb://localhost:27017')
app.config['MONGO_DB']		= os.getenv('MONGO_DB',		'backend')
app.config['REDIS_URL'] 	= os.getenv('REDIS_URL',	'redis://localhost:6379')
app.config['REDIS_DB']		= int(os.getenv('REDIS_DB',		'0'))
app.config['DEBUG']			= bool(os.getenv('DEBUG', True))
app.config['TESTING']		= bool(os.getenv('TESTING', False))
app.config['PRODUCTION']	= bool(os.getenv('PRODUCTION', False))
app.config['STRIPE_KEY']	= os.getenv('STRIPE_KEY', '')

def start():
	print("Booting up...")

	mongoengine.connect(app.config['MONGO_DB'], host=app.config['MONGO_URL'])
	print("Connected to Mongo")


	global sessions
	sessions = redis.from_url(app.config['REDIS_URL'], db=app.config['REDIS_DB'])
	sessions.set('testing-redis', 'test')
	test = sessions.get('testing-redis')
	assert test == 'test', "ERROR: Redis not working!"
	print("Connected to Redis")

	global AuthBlueprint
	AuthBlueprint = Blueprint('auth', __name__)
	global EventBlueprint
	EventBlueprint = Blueprint('events', __name__)
	global ProjectBlueprint
	ProjectBlueprint = Blueprint('projects', __name__)
	global UserBlueprint
	UserBlueprint = Blueprint('users', __name__)

	from backend.controllers import auth, users, events, registration, posts, projects, users

	app.register_blueprint(AuthBlueprint, url_prefix="/auth")
	app.register_blueprint(EventBlueprint, url_prefix="/events")
	app.register_blueprint(ProjectBlueprint, url_prefix="/projects")
	app.register_blueprint(UserBlueprint, url_prefix="/users")
	
	# print(app.url_map)

	@app.route('/')
	def index():
		return "OK"

	@app.errorhandler(404)
	def pageNotFound(error):
		return "Page not found :("

	@app.errorhandler(500)
	def serverError(error):
		return error

	print("App Booted!")

## CORS stuff

def crossdomain(origin=None, methods=None, headers=None,
				max_age=21600, attach_to_all=True,
				automatic_options=True):
	if methods is not None:
		methods = ', '.join(sorted(x.upper() for x in methods))
	if headers is not None and not isinstance(headers, basestring):
		headers = ', '.join(x.upper() for x in headers)
	if not isinstance(origin, basestring):
		origin = ', '.join(origin)
	if isinstance(max_age, timedelta):
		max_age = max_age.total_seconds()

	def get_methods():
		if methods is not None:
			return methods

		options_resp = app.make_default_options_response()
		return options_resp.headers['allow']

	def decorator(f):
		def wrapped_function(*args, **kwargs):
			if automatic_options and request.method == 'OPTIONS':
				resp = app.make_default_options_response()
			else:
				resp = make_response(f(*args, **kwargs))
			if not attach_to_all and request.method != 'OPTIONS':
				return resp

			h = resp.headers

			h['Access-Control-Allow-Origin'] = origin
			h['Access-Control-Allow-Methods'] = get_methods()
			h['Access-Control-Max-Age'] = str(max_age)
			if headers is not None:
				h['Access-Control-Allow-Headers'] = headers
			return resp

		f.provide_automatic_options = False
		f.required_methods = ['OPTIONS']
		return update_wrapper(wrapped_function, f)
	return decorator

@app.before_request
def option_autoreply():
    """ Always reply 200 on OPTIONS request """

    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()

        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']

        h = resp.headers

        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        # We also keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers

        return resp

# @app.after_request
# def set_allow_origin(resp):
#     """ Set origin for GET, POST, PUT, DELETE requests """

#     h = resp.headers

#     # Allow crossdomain for other HTTP Verbs
#     if request.method != 'OPTIONS' and 'Origin' in request.headers:
#         h['Access-Control-Allow-Origin'] = request.headers['Origin']


#     return resp


if app.config['PRODUCTION']:
	start()
elif __name__ == '__main__':
	start()
	app.run()