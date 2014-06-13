from flask import Flask, request
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient("localhost", 27017)
app.db = client.backend

db = app.db
students = db.students
mentors = db.mentors

@app.route('/')
def hello_world():
    return 'Hello World!'


import mongoExample
mongoExample.init(app)
