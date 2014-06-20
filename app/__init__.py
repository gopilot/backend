from flask import Flask, request, render_template
import os
import pymongo
import redis
from urlparse import urlparse

app = Flask(__name__)

mongo_url = urlparse( os.getenv("MONGOHQ_URL", "mongodb://localhost:27017/backend") )

mongo_db = mongo_url.path.replace('/', '')
mongo_client = pymongo.MongoClient( mongo_url.geturl() )
db = mongo_client[mongo_db]


redis_url = urlparse( os.getenv("REDISCLOUD_URL", "redis://localhost:6379") )
sessions = redis.Redis(host=redis_url.hostname, port=redis_url.port, password=redis_url.password)

from auth import auth
app.register_blueprint(auth)

from users import users
app.register_blueprint(users, url_prefix="/users")

from events import events
app.register_blueprint(events, url_prefix="/events")


@app.route('/')
def index():
  return render_template("index.html")
