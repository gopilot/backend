from flask import Flask, request, render_template
import os
import pymongo
import redis
from urlparse import urlparse

app = Flask(__name__)

app.config['MONGO_URL'] = os.getenv('MONGO_URL',	'mongodb://localhost:27017')
app.config['MONGO_DB']	= os.getenv('MONGO_DB',		'backend')
app.config['REDIS_URL'] = os.getenv('REDIS_URL',	'redis://localhost:6379')
app.config['REDIS_DB']	= os.getenv('REDIS_DB',		'0')
app.config['DEBUG']			= bool(os.getenv('DEBUG', True))
app.config['TESTING']		= bool(os.getenv('TESTING', False))
print app.config

mongo_url = urlparse( app.config['MONGO_URL'] )

global mongo_client
mongo_client = pymongo.MongoClient( mongo_url.geturl() )

global db
db = mongo_client[ app.config['MONGO_DB']]

redis_url = urlparse( app.config['REDIS_URL'] )

global sessions
sessions = redis.Redis(host=redis_url.hostname, port=redis_url.port, password=redis_url.password, db=app.config['REDIS_DB'])

from auth import auth
app.register_blueprint(auth)

from users import users
app.register_blueprint(users, url_prefix="/users")

from events import events
app.register_blueprint(events, url_prefix="/events")

@app.route('/')
def index():
	return render_template("index.html")
