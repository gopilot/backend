from flask import Flask, request, render_template
import os
import pymongo
import redis
from urlparse import urlparse

app = Flask(__name__)

app.config['MONGO_URL'] = os.getenv('MONGO_URL',	'mongodb://localhost:27017')
app.config['MONGO_DB']	= os.getenv('MONGO_DB',		'backend')
app.config['REDIS_URL'] = os.getenv('REDIS_URL',	'redis://localhost:6379')
app.config['REDIS_DB']	= int(os.getenv('REDIS_DB',		'0'))
app.config['DEBUG']			= bool(os.getenv('DEBUG', True))
app.config['TESTING']		= bool(os.getenv('TESTING', False))
print app.config
print 'start mongo'
mongo_url = urlparse( app.config['MONGO_URL'] )
print 'mongo url'
mongo_client = pymongo.MongoClient( mongo_url.geturl() )
print 'mongo client'
db = mongo_client[ app.config['MONGO_DB']]
print 'mongo db'
redis_url = urlparse( app.config['REDIS_URL'] )
print 'redis url'
sessions = redis.Redis(host=redis_url.hostname, port=redis_url.port, password=redis_url.password, db=app.config['REDIS_DB'])
print 'sessions'
## Used by tests to change databases after updating config values
def update_dbs():
	global db
	db = mongo_client[ app.config['MONGO_DB'] ]
	global sessions
	sessions = redis.Redis(host=redis_url.hostname, port=redis_url.port, password=redis_url.password, db=app.config['REDIS_DB'])

print 'set up dbs'

from auth import auth as AuthBlueprint
app.register_blueprint(AuthBlueprint)

from users import users as UserBlueprint
app.register_blueprint(UserBlueprint, url_prefix="/users")

from events import events as EventBlueprint
app.register_blueprint(EventBlueprint, url_prefix="/events")

print "registered blueprints"

@app.route('/')
def index():
	print 'in index'
	return render_template("index.html")
