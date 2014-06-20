from flask import Flask

import app as backend

import unittest

import json
import pymongo
import redis
import time

backend.init_app('app.config.TestingConfig')
test_client = backend.app.test_client()

class BackendAuthTests(unittest.TestCase):
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
		self.test_token = self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=data).data

	## Clears database and redis connection after each test
	def tearDown(self):
		backend.mongo_client.drop_database('backend_test')
		backend.sessions.flushdb()
		print 'Completed test:', str(time.clock() - self.start_time)+'s'

	## Test the debug_token endpoint	
	def test_debug_token(self):
		response = self.app.get('/debug_token?session='+self.test_token)
		assert response.data == 'Valid token'

	## Test the debug_token endpoint with a bad token
	def test_debug_token_fail(self):
		response = self.app.get('/debug_token?session=X'+self.test_token)
		assert response.data == 'Invalid token'

	## Test the signup
	def test_signup(self):
		data = json.dumps({
			'name': 'Test Signup',
			'email': 'test-signup@gopilot.org', 
			'password': 'test',
			'type': 'student'
		})
		response = self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=data)
		assert len(response.data) > 0

		token_debug = self.app.get('/debug_token?session='+response.data)
		assert token_debug.data == 'Valid token'

	## Test the signup, reusing the email from above.
	def test_signup_repeat(self):
		data2 = json.dumps({
			'name': 'Test User 2',
			'email': 'test@gopilot.org', 
			'password': 'test',
			'type': 'student'
		})
		response = self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=data2)

		assert response.data == 'Email already exists'

	## Test the login
	def test_login(self):
		data = json.dumps({
			'email': 'test@gopilot.org',
			'password': 'test'
		})
		response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=data)
		assert len(response.data) > 0

		token_debug = self.app.get('/debug_token?session='+response.data)
		assert token_debug.data == 'Valid token'

	## Test login, with a bad email
	def test_login_fail_email(self):
		data = json.dumps({
			'email': 'Xtest@gopilot.org',
			'password': 'test'
		})
		response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=data)
		assert response.data == 'Email not found'

	## Test login, with a bad password
	def test_login_fail_password(self):
		data = json.dumps({
			'email': 'test@gopilot.org',
			'password': 'Xtest'
		})
		response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=data)
		assert response.data == 'Incorrect password'

if __name__ == '__main__':
    unittest.main()
