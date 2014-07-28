import unittest
import json
import pymongo
import redis
import time
import datetime

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
