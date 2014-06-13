from flask import Flask, request
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient("localhost", 27017)
db = client.backend

import routes
import mongoExample
