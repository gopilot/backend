from flask import Flask, request
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient("localhost", 27017)
db = client.backend

# Config variables
Flask.secret_key = 'a091jv730bnsqf92pt893bndsk' # super-random string

from auth import auth
app.register_blueprint(auth)

from users import users
app.register_blueprint(users, url_prefix="/users")

from events import events
app.register_blueprint(events, url_prefix="/events")

