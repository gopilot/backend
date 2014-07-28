from flask import Flask

import app as backend

import unittest

import json
import pymongo
import redis
import time
import datetime


backend.app.config['MONGO_DB'] = 'backend_test'
backend.app.config['REDIS_DB'] = 15
backend.start()
test_client = backend.app.test_client()

class AuthTests(unittest.TestCase):
	## Creates one user before every test
	def setUp(self):
		self.start_time = time.clock()
		self.app = test_client
		data = json.dumps({
			'name': 'Main user',
			'email': 'test@gopilot.org',
			'password': 'test',
			'type': 'student'
		})
		self.test_token = self.app.post('/users', headers={'Content-Type': 'application/json'}, data=data).data

	## Clears database and redis connection after each test
	def tearDown(self):
		backend.mongo_client.drop_database('backend_test')
		backend.sessions.flushdb()
		
	## Test the check_session endpoint	
	def test_check_session(self):
		response = self.app.get('/auth/check_session?session='+self.test_token)
		assert response.data == 'true'

	## Test the check_session endpoint with a bad token
	def test_check_session_fail(self):
		response = self.app.get('/auth/check_session?session=X'+self.test_token)
		assert response.data == 'false'

	def test_retrieve_user(self):
		response = self.app.get('/auth/retrieve_user?session='+self.test_token)
		assert json.loads(response.data)['name'] == 'Main user'

	def test_retrieve_user_fail(self):
		response = self.app.get('/auth/retrieve_user?session=X'+self.test_token)
		assert response.data == 'Session invalid'

	## Test the login
	def test_login(self):
		data = json.dumps({
			'email': 'test@gopilot.org',
			'password': 'test'
		})
		response = self.app.post('/auth/login', headers={'Content-Type': 'application/json'}, data=data).data
		response = json.loads(response)
		assert len(response['session']) > 0
		assert response['user']['name'] == 'Main user'

		token_debug = self.app.get('/auth/check_session?session='+response['session'])
		assert token_debug.data == 'true'

	## Test login, with a bad email
	def test_login_fail_email(self):
		data = json.dumps({
			'email': 'Xtest@gopilot.org',
			'password': 'test'
		})
		response = self.app.post('/auth/login', headers={'Content-Type': 'application/json'}, data=data)
		assert response.data == 'Email not found'

	## Test login, with a bad password
	def test_login_fail_password(self):
		data = json.dumps({
			'email': 'test@gopilot.org',
			'password': 'Xtest'
		})
		response = self.app.post('/auth/login', headers={'Content-Type': 'application/json'}, data=data)
		assert response.data == 'Incorrect password'

class EventTests(unittest.TestCase):
	def setUp(self):
		self.start_time = time.clock()
		self.app = test_client

		## Create test organizer
		data = json.dumps({
			'name': 'Main Organizer',
			'email': 'organizer@gopilot.org',
			'password': 'test',
			'type': 'organizer'
		})
		self.organizer_token = self.app.post('/users', headers={'Content-Type': 'application/json'}, data=data).data

		data = json.dumps({
			'name': 'Test Event',
			'start_date': str(datetime.datetime.today()),
			'end_date': str(datetime.datetime.today() + datetime.timedelta(days=1)),
			'location': 'Tech Inc. HQ',
			'address': '1111 Random Way, Townville, CA'
		})
		self.test_event = self.app.post('/events?session='+self.organizer_token, headers={'Content-Type': 'application/json'}, data=data).data

	## Clears database and redis connection after each test
	def tearDown(self):
		backend.mongo_client.drop_database('backend_test')
		backend.sessions.flushdb()

	def test_create_event(self):
		data = json.dumps({
			'name': 'Test Event',
			'start_date': str(datetime.datetime.today()),
			'end_date': str(datetime.datetime.today() + datetime.timedelta(days=1)),
			'location': 'Tech Inc. HQ',
			'address': '1111 Random Way, Townville, CA',
			'image': 'http://placekitten.com/400/400'
		})
		response = self.app.post('/events?session='+self.organizer_token, headers={'Content-Type': 'application/json'}, data=data)
		assert len(response.data) > 20
	def test_update_event(self):
		data = json.dumps({
			'name': 'Renamed Event'
		})
		response = self.app.put('/events/'+self.test_event+'?session='+self.organizer_token, headers={'Content-Type': 'application/json'}, data=data)
		assert json.loads(response.data)['name'] == 'Renamed Event'

	def test_get_event(self):
		response = self.app.get('/events/'+self.test_event+'?session='+self.organizer_token)
		assert json.loads(response.data)['name'] == 'Test Event'

	def test_get_all_events(self):
		response = self.app.get('/events')
		assert len( json.loads(response.data) ) > 0

	def test_delete_event(self):
		response = self.app.delete('/events/'+self.test_event+'?session='+self.organizer_token)
		assert response.data == 'Event deleted'

class UserTests(unittest.TestCase):
	def setUp(self):
		self.start_time = time.clock()
		self.app = test_client
		data = json.dumps({
			'name': 'Main user',
			'email': 'test@gopilot.org',
			'password': 'test',
			'type': 'student'
		})
		self.test_token = self.app.post('/users', headers={'Content-Type': 'application/json'}, data=data).data
		self.test_user = json.loads( self.app.get('/auth/retrieve_user?session='+self.test_token).data )['_id']
		
		## Create test organizer
		organizer_data = json.dumps({
			'name': 'Main Organizer',
			'email': 'organizer@gopilot.org',
			'password': 'test',
			'type': 'organizer'
		});
		self.organizer_token = self.app.post('/users', headers={'Content-Type': 'application/json'}, data=organizer_data).data
		self.test_organizer = json.loads( self.app.get('/auth/retrieve_user?session='+self.organizer_token).data )['_id']
		

	## Clears database and redis connection after each test
	def tearDown(self):
		backend.mongo_client.drop_database('backend_test')
		backend.sessions.flushdb()

	## Test the signup
	def test_signup(self):
		data = json.dumps({
			'name': 'Test Signup',
			'email': 'test-signup@gopilot.org', 
			'password': 'test',
			'type': 'student'
		})
		response = self.app.post('/users', headers={'Content-Type': 'application/json'}, data=data)
		assert len(response.data) > 0

		token_debug = self.app.get('/auth/check_session?session='+response.data)
		assert token_debug.data == 'true'

	## Test the signup, reusing the email from above.
	def test_signup_repeat(self):
		data2 = json.dumps({
			'name': 'Test User 2',
			'email': 'test@gopilot.org', 
			'password': 'test',
			'type': 'student'
		})
		response = self.app.post('/users', headers={'Content-Type': 'application/json'}, data=data2)
		assert response.data == 'Email already exists'

	def test_get_user(self):
		response = self.app.get('/users/'+self.test_user+'?session='+self.test_token)
		assert json.loads(response.data)['name'] == 'Main user'

	def test_get_all_user(self):
		response = self.app.get('/users?session='+self.organizer_token)
		assert len( json.loads(response.data) ) > 0

	def test_update_user(self):
		data = json.dumps({
			'name': 'Updated User'
		})
		response = self.app.put('/users/'+self.test_user+'?session='+self.test_token, headers={'Content-Type': 'application/json'}, data=data)
		assert json.loads(response.data)['name'] == 'Updated User'

	def test_update_user_with_organizer(self):
		data = json.dumps({
			'name': 'Updated User1'
		})
		response = self.app.put('/users/'+self.test_user+'?session='+self.organizer_token, headers={'Content-Type': 'application/json'}, data=data)
		assert json.loads(response.data)['name'] == 'Updated User1'

	def test_update_user_with_bad_token(self):
		data = json.dumps({
			'name': 'Updated User1'
		})
		response = self.app.put('/users/'+self.test_organizer+'?session='+self.test_token, headers={'Content-Type': 'application/json'}, data=data)
		assert response.data == "Unauthorized request: You don't have permission for this action"


	def test_delete_user(self):
		response = self.app.delete('/users/'+self.test_user+'?session='+self.test_token)
		assert response.data == 'User deleted'

	def test_delete_user_with_organizer(self):
		response = self.app.delete('/users/'+self.test_user+'?session='+self.organizer_token)
		assert response.data == 'User deleted'

	def test_delete_user_with_bad_token(self):
		response = self.app.delete('/users/'+self.test_organizer+'?session='+self.test_token)
		assert response.data == "Unauthorized request: You don't have permission for this action"


if __name__ == '__main__':
    unittest.main()
