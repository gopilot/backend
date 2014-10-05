from flask import Flask, request, render_template, json, Blueprint
import os
import sys
import pymongo
import redis
import mongoengine
from bson.objectid import ObjectId
import logging

app = Flask(__name__)
app.debug = True

app.config['MONGO_URL'] = os.getenv('MONGO_URL',	'mongodb://localhost:27017')
app.config['MONGO_DB']	= os.getenv('MONGO_DB',		'backend')
app.config['REDIS_URL'] = os.getenv('REDIS_URL',	'redis://localhost:6379')
app.config['REDIS_DB']	= int(os.getenv('REDIS_DB',		'0'))
app.config['DEBUG']			= bool(os.getenv('DEBUG', True))
app.config['TESTING']		= bool(os.getenv('TESTING', False))
app.config['PRODUCTION']	= bool(os.getenv('PRODUCTION', False))


def start():
	print("Booting up...")

	# Configure logging.
	app.logger.setLevel(logging.DEBUG)
	del app.logger.handlers[:]
	handler = logging.StreamHandler(stream=sys.stdout)
	handler.setLevel(logging.DEBUG)
	handler.formatter = logging.Formatter(
	    fmt=u"%(asctime)s level=%(levelname)s %(message)s",
	    datefmt="%Y-%m-%dT%H:%M:%SZ",
	)
	app.logger.addHandler(handler)



	mongoengine.connect(app.config['MONGO_DB'], host=app.config['MONGO_URL'])
	print("Connected to mongo")


	global sessions
	sessions = redis.from_url(app.config['REDIS_URL'])
	print("Connected to Redis")
	sessions.set('testing-redis', 'test')
	test = sessions.get('testing-redis')
	if test != 'test':
		print("ERROR: REDIS NOT WORKING!!")

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

if app.config['PRODUCTION']:
	start()
elif __name__ == '__main__':
	start()
	app.run()