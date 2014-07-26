from flask import Flask, request, render_template, json
import os
import pymongo
import redis
import models.humongolus as orm
from urlparse import urlparse
from bson.objectid import ObjectId

app = Flask(__name__)

app.config['MONGO_URL'] = os.getenv('MONGO_URL',	'mongodb://localhost:27017')
app.config['MONGO_DB']	= os.getenv('MONGO_DB',		'backend')
app.config['REDIS_URL'] = os.getenv('REDIS_URL',	'redis://localhost:6379')
app.config['REDIS_DB']	= int(os.getenv('REDIS_DB',		'0'))
app.config['DEBUG']			= bool(os.getenv('DEBUG', True))
app.config['TESTING']		= bool(os.getenv('TESTING', False))
#print app.config

mongo_client = pymongo.MongoClient( app.config['MONGO_URL'] )
db = mongo_client[ app.config['MONGO_DB'] ]
redis_url = urlparse( app.config['REDIS_URL'] )
sessions = redis.Redis(host=redis_url.hostname, port=redis_url.port, password=redis_url.password, db=app.config['REDIS_DB'])

orm.settings( mongo_client )

## Used by tests to change databases after updating config values
def update_dbs():
	global db
	db = mongo_client[ app.config['MONGO_DB'] ]
	global sessions
	sessions = redis.Redis(host=redis_url.hostname, port=redis_url.port, password=redis_url.password, db=app.config['REDIS_DB'])

from auth import auth as AuthBlueprint
app.register_blueprint(AuthBlueprint, url_prefix="/auth")

from users import users as UserBlueprint
app.register_blueprint(UserBlueprint, url_prefix="/users")

from events import events as EventBlueprint
app.register_blueprint(EventBlueprint, url_prefix="/events")

@app.route('/')
def index():
	return render_template("index.html")
