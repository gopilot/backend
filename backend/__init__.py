print("Starting app...")
from flask import Flask, request, render_template, json, Blueprint, make_response
import os
import sys
import redis
import traceback
import mongoengine
from bson.objectid import ObjectId
import logging
import socket

from logging.handlers import SysLogHandler

from datetime import timedelta
from functools import update_wrapper
from pprint import pprint

app = Flask(__name__)
app.debug = True

app.config['MONGO_URL'] 	= os.getenv('MONGO_URL',	'mongodb://localhost:27017')
app.config['MONGO_DB']		= os.getenv('MONGODB_DATABASE', 'backend')
app.config['MONGO_USER']	= os.getenv('MONGODB_USERNAME', "")
app.config['MONGO_PASS']	= os.getenv('MONGODB_PASSWORD', "")
app.config['MONGO_HOST']	= os.getenv('MONGODB_HOST', "")
app.config['MONGO_PORT']	= int(os.getenv('MONGODB_PORT', 27017))

app.config['REDIS_URL']		= os.getenv('REDIS_URL', 'redis://localhost:6379')
app.config['REDIS_DB']		= int(os.getenv('REDIS_DB',		"0"))

app.config['DEBUG']			= bool(os.getenv('DEBUG', True))
app.config['TESTING']		= bool(os.getenv('TESTING', False))
app.config['PRODUCTION']	= bool(os.getenv('PRODUCTION', False))

app.config['STRIPE_KEY']	= os.getenv('STRIPE_KEY', '[ERROR]')
app.config['SENDGRID_PASS'] = os.getenv('SENDGRID_PASS', '[ERROR]')
app.config['TWITTER_TOKEN'] = os.getenv('TWITTER_TOKEN', '[ERROR]')
app.config['TOPSY_KEY']		= os.getenv('TOPSY_KEY', '[ERROR]')

app.config['AZURE_NAME']	= os.getenv('AZURE_NAME', '[ERROR]')
app.config['AZURE_KEY']		= os.getenv('AZURE_KEY', '[ERROR]')
app.config['AZURE_URL']		= os.getenv('AZURE_URL', 'https://files.gopilot.org/user-files/')



app.config['PROPAGATE_EXCEPTIONS'] = True

app.debug = False

ADMINS = ['peter@gopilot.org']

jsonType = {'Content-Type': 'application/json'}


def init_logging(app):
	print("init logging");
	papertrail = SysLogHandler(address=('logs2.papertrailapp.com', 16656))
	formatter = logging.Formatter('%(asctime)s api.gopilot.org %(filename)s%(lineno)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
	papertrail.setFormatter(formatter)
	app.logger.addHandler(papertrail)
	app.logger.setLevel(logging.INFO)

def start():
	print("Booting up...")
	print("Testing:    %s" % app.config['TESTING'])
	print("Production: %s" % app.config['PRODUCTION'])
	

	global sessions
	print("Trying to connect to Redis:")
	print('\t URL: %s' % app.config['REDIS_URL'])
	print('\t DB: %s' % app.config['REDIS_DB'])
	try:
		sessions = redis.from_url(app.config['REDIS_URL'], db=app.config['REDIS_DB'])
	except Exception as e:
		print("Unexpected redis error: %s" % e)
	
	print("Testing Redis...")
	print("Testing session set")
	try:
		sessions.set('testing-redis', 'test')
	except Exception as e:
		print("Redis error while setting %s" % e)
	
	print('Testing session get')
	test = None
	try:
		test = sessions.get('testing-redis')
	except Exception as e:
		print("Redis error while setting %s" % e)
	
	if(test != 'test'):
		print("ERROR: Redis not working!")
	
	print("Connected to Redis")

	print("Trying to connect to Mongo:")
	print('\t DB: %s' % app.config['MONGO_DB'])
	print('\t Host: %s' % app.config['MONGO_HOST'])
	print('\t Username: %s' % app.config['MONGO_USER'])
	print('\t Password: %s' % app.config['MONGO_PASS'])
	
	try:
		mongoengine.connect(app.config['MONGO_DB'], host=app.config['MONGO_HOST'], username=app.config['MONGO_USER'], password=app.config['MONGO_PASS'])
	except Exception as e:
		print("Mongo error %s" % e)
		app.logger.error("Unexpected mongo error: %s" % e)

	print("Connected to Mongo")

	global AuthBlueprint
	AuthBlueprint = Blueprint('auth', __name__)
	global EventBlueprint
	EventBlueprint = Blueprint('events', __name__)
	global ProjectBlueprint
	ProjectBlueprint = Blueprint('projects', __name__)
	global UserBlueprint
	UserBlueprint = Blueprint('users', __name__)

	@app.route('/')
	def index():
		return "OK"

	@app.errorhandler(404)
	def pageNotFound(error):
		return "Page not found...", 404

	@app.errorhandler(500)
	def serverError(error):
		app.logger.error(error)
		return "ERROR"

	@app.errorhandler(Exception)
	def defaultHandler(e):
		app.logger.error("Exception: %s", e)
		app.logger.error(traceback.format_exc())
		print(traceback.format_exc())
		return json.dumps({
            "status": "failed",
            "reason": "error",
            "message": "Uh oh, something went wrong..."
        }), 500, jsonType

	from backend.controllers import auth, users, events, registration, discounts, posts, projects, users, scheduleItems
	
	app.register_blueprint(AuthBlueprint, url_prefix="/auth")
	app.register_blueprint(EventBlueprint, url_prefix="/events")
	app.register_blueprint(ProjectBlueprint, url_prefix="/projects")
	app.register_blueprint(UserBlueprint, url_prefix="/users")
	
	if app.config['PRODUCTION']:
		init_logging(app)
		app.logger.info(20*"-" + " App Booted " + 20*"-")

	print("App Booted!!")


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

@app.after_request
def set_allow_origin(resp):
	""" Set origin for GET, POST, PUT, DELETE requests """

	h = resp.headers

	# Allow crossdomain for other HTTP Verbs
	if request.method != 'OPTIONS' and 'Origin' in request.headers:
		h['Access-Control-Allow-Origin'] = request.headers['Origin']

	return resp


def send_error(msg, status):
	return json.dumps({
		"error": True,
		"status": status,
		"message": msg
	}), status, {'Content-Type': 'application/json'}

if app.config['PRODUCTION']:
	start()
elif __name__ == '__main__':
	start()
	app.run()