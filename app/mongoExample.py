###
# For those looking to learn MongoDB, http://api.mongodb.org/python/current/tutorial.html is highly suggested reading.
###

from flask import Flask, request
from app import app, db
import pymongo

# GET /save?value=[value] - Saves a value in the DB
@app.route('/save')
def set_value():
	if not request.args.get('value'):
		return "The 'value' parameter is required"
	val = request.args.get('value')
	db.test_collection.insert({'value': val})
	return "Value saved"

# GET /find?query=[queryString] - Returns all values containing queryString
# GET /find?match=[matchString] - Returns all values matching matchString
# GET /find - Returns all values in the DB
@app.route('/find')
def get_value():
	if request.args.get('query'):
		results = db.test_collection.find({ 'value': { '$regex': request.args.get('query') } })
	elif request.args.get('match'):
		results = db.test_collection.find({ 'value': request.args.get('match') })
	else:
		results = db.test_collection.find() # Find defaults to return all objects in collection

	str = ''
	for item in results:
		str += item['value']+'<br>'

	if len(str) == 0:
		str = "No results"

	return str