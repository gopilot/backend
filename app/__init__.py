from flask import Flask, request, render_template, json
import os
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
#print app.config

def start():
	global sessions
	print "STARTING", app.config['MONGO_DB'], app.config['MONGO_URL'], app.config['REDIS_DB'], app.config['REDIS_URL']
	mongoengine.connect(app.config['MONGO_DB'], host=app.config['MONGO_URL'])
	print "Connected to mongo"
	sessions = redis.from_url(app.config['REDIS_URL'])
	print "Connected to Redis"
	from auth import auth as AuthBlueprint
	app.register_blueprint(AuthBlueprint, url_prefix="/auth")
	print "Auth"
	from users import users as UserBlueprint
	app.register_blueprint(UserBlueprint, url_prefix="/users")
	print "users"
	from events import events as EventBlueprint
	from events import registration
	from events import posts
	app.register_blueprint(EventBlueprint, url_prefix="/events")
	print "events"
	from projects import projects as ProjectBlueprint
	app.register_blueprint(ProjectBlueprint, url_prefix="/projects")
	print "projects"
	@app.route('/')
	def index():
		return render_template("index.html")
	print "Done!"