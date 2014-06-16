from flask import Flask, request
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient("localhost", 27017)
db = client.backend

# Config variables
Flask.secret_key = 'a091jv730bnsqf92pt893bndsk' # super-random string

import routes
#import mongoExample
