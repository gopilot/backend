from flask import Flask, request, render_template, json, Blueprint
import os
import sys
import pymongo
import redis
import mongoengine
from bson.objectid import ObjectId

app = Flask(__name__)

app.config['MONGO_URL'] = os.getenv('MONGO_URL',	'mongodb://localhost:27017')
app.config['MONGO_DB']	= os.getenv('MONGO_DB',		'backend')
app.config['REDIS_URL'] = os.getenv('REDIS_URL',	'redis://localhost:6379')
app.config['REDIS_DB']	= int(os.getenv('REDIS_DB',		'0'))
app.config['DEBUG']			= bool(os.getenv('DEBUG', True))
app.config['TESTING']		= bool(os.getenv('TESTING', False))
app.config['PRODUCTION']	= bool(os.getenv('PRODUCTION', False))


def start():
	global sessions
	print("STARTING", app.config['MONGO_DB'], app.config['MONGO_URL'], app.config['REDIS_DB'], app.config['REDIS_URL'])
	mongoengine.connect(app.config['MONGO_DB'], host=app.config['MONGO_URL'])
	print("Connected to mongo")
	sessions = redis.from_url(app.config['REDIS_URL'])
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
		return render_template("index.html")
	print("Done!")

print(__name__)
if app.config['PRODUCTION']:
	start()