from flask import Flask, request
import os
import pymongo

app = Flask(__name__)

mongo_uri = os.getenv("MONGOHQ_URL", "mongodb://localhost:27017/backend")

mongo_db = mongo_uri.split("/")[-1]

client = pymongo.MongoClient(mongo_uri)
db = client[mongo_db]

# Config variables
Flask.secret_key = 'a091jv730bnsqf92pt893bndsk' # super-random string

import routes
#import mongoExample
