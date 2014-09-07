import unittest
import json
import pymongo
import redis
import time
import datetime

from . import test_client, redis_client, mongo_client

def h(session=None):
    headers = {'Content-Type': 'application/json'}
    if session:
        headers['session'] = session    
    return headers

class UserTests(unittest.TestCase):
    def setUp(self):
        mongo_client.drop_database('backend_test')
        redis_client.flushdb()

        self.start_time = time.clock()
        self.app = test_client
        data = json.dumps({
            'name': 'Main user',
            'email': 'test@gopilot.org',
            'password': 'test-test',
            'type': 'student'
        })
        self.test_token = json.loads( self.app.post('/users', headers=h(), data=data).data.decode('utf-8') )['session']
        self.test_user = json.loads( self.app.get('/auth/retrieve_user', headers=h(session=self.test_token)).data.decode('utf-8') )['id']
        
        ## Create test organizer
        organizer_data = json.dumps({
            'name': 'Main Organizer',
            'email': 'organizer@gopilot.org',
            'password': 'test-test',
            'type': 'organizer'
        });
        self.organizer_token = json.loads( self.app.post('/users', headers=h(), data=organizer_data).data.decode('utf-8') )['session']
        self.test_organizer = json.loads( self.app.get('/auth/retrieve_user', headers=h(session=self.organizer_token)).data.decode('utf-8') )['id']

    ## Test the signup
    def test_signup(self):
        data = json.dumps({
            'name': 'Test Signup',
            'email': 'test-signup@gopilot.org', 
            'password': 'test-test',
            'type': 'student'
        })
        response = self.app.post('/users', headers=h(), data=data)
        assert len(response.data.decode('utf-8')) > 0
        sess = json.loads(response.data.decode('utf-8'))['session']
        token_debug = self.app.get('/auth/check_session', headers=h(session=sess))
        assert token_debug.data.decode('utf-8') == 'true'

    ## Test the signup, reusing the email from above.
    def test_signup_repeat(self):
        data2 = json.dumps({
            'name': 'Test User 2',
            'email': 'test@gopilot.org', 
            'password': 'test-test',
            'type': 'student'
        })
        response = self.app.post('/users', headers=h(), data=data2)
        assert response.data.decode('utf-8') == 'Email already exists'

    def test_get_user(self):
        response = self.app.get('/users/'+self.test_user, headers=h(session=self.test_token))
        assert json.loads(response.data.decode('utf-8'))['name'] == 'Main user'

    def test_get_all_user(self):
        response = self.app.get('/users', headers=h(session=self.organizer_token))
        assert len( json.loads(response.data.decode('utf-8')) ) > 0

    def test_update_user(self):
        data = json.dumps({
            'name': 'Updated User'
        })
        response = self.app.put('/users/'+self.test_user, headers=h(session=self.test_token), data=data)
        assert json.loads(response.data.decode('utf-8'))['name'] == 'Updated User'

    def test_update_user_with_organizer(self):
        data = json.dumps({
            'name': 'Updated User1'
        })
        response = self.app.put('/users/'+self.test_user, headers=h(session=self.organizer_token), data=data)
        assert json.loads(response.data.decode('utf-8'))['name'] == 'Updated User1'

    def test_update_user_with_bad_token(self):
        data = json.dumps({
            'name': 'Updated User1'
        })
        response = self.app.put('/users/'+self.test_organizer, headers=h(session=self.test_token), data=data)
        assert response.data.decode('utf-8') == "Unauthorized request: You don't have permission for this action"


    def test_delete_user(self):
        response = self.app.delete('/users/'+self.test_user, headers=h(session=self.test_token))
        assert response.data.decode('utf-8') == 'User deleted'

    def test_delete_user_with_organizer(self):
        response = self.app.delete('/users/'+self.test_user, headers=h(session=self.organizer_token))
        assert response.data.decode('utf-8') == 'User deleted'

    def test_delete_user_with_bad_token(self):
        response = self.app.delete('/users/'+self.test_organizer, headers=h(session=self.test_token))
        assert response.data.decode('utf-8') == "Unauthorized request: You don't have permission for this action"

if __name__ == '__main__':
    unittest.main()