import app as backend

import unittest

import json
import pymongo
import redis
import time

class BackendAuthTests(unittest.TestCase):
	def setUp(self):
		backend.db = pymongo.MongoClient( 'mongodb://localhost:27017/backend_test' )
		backend.sessions = redis.Redis(host='localhost', port='6379', db=15)
		self.app = backend.app.test_client()
		data = json.dumps({
			'name': 'Main user',
			'email': 'test1@gopilot.org',
			'password': 'test',
			'type': 'student'
		})
		self.user_token = self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=data).data

	def tearDown(self):
		print 'cleaning up!'
		time.sleep(60)
		backend.db.drop_database('backend_test')
		backend.sessions.flushdb()
		time.sleep(60)

	def test_debug_token(self):
		debug = self.app.get('/debug_token?token='+self.user_token)
		print "debug", self.user_token
		print debug.data
		assert debug.data == 'Valid token'

	def test_debug_token_fail(self):
		debug = self.app.get('/debug_token?token=X'+self.user_token)
		assert debug.data == 'Invalid token'

	def test_signup(self):
		data = json.dumps({
			'name': 'Test user',
			'email': 'test-signup@gopilot.org', 
			'password': 'test',
			'type': 'student'
		})
		token = self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=data)
		assert len(token.data) > 0
		debug = self.app.get('/debug_token?token='+token.data)

		print "signup", token.data
		print debug.data

		assert debug.data == 'Valid token'

	def test_signup_repeat(self):
		data = json.dumps({
			'name': 'Test User',
			'email': 'testrepeat@example.com', 
			'password': 'test',
			'type': 'student'
		})
		self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=data)

		data2 = json.dumps({
			'name': 'Test User 2',
			'email': 'testrepeat@example.com', 
			'password': 'test',
			'type': 'student'
		})
		signup = self.app.post('/signup', data=data2)

		print "existing"
		print signup.data
		assert signup.data == 'Email already exists'

	def test_login(self):
		data = json.dumps({
			'email': 'test@gopilot.org',
			'password': 'test'
		})
		token = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=data)
		assert len(token.data) > 0
		debug = self.app.get('/debug_token?token='+token.data)
		assert debug.data == 'Valid token'

	def test_login_fail_email(self):
		data = json.dumps({
			'email': 'Xtest@gopilot.org',
			'password': 'test'
		})
		login = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=data)
		assert login.data == 'Email not found'

	def test_login_fail_password(self):
		data = json.dumps({
			'email': 'test@gopilot.org',
			'password': 'Xtest'
		})
		login = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=data)
		assert login.data == 'Incorrect password'

if __name__ == '__main__':
    unittest.main()

