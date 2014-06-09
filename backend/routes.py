from flask import Flask, render_template, request, redirect
import os
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/index', methods=['GET'])
def index():
	return render_template('index.html')

if __name__ == '__main__':
    app.run()