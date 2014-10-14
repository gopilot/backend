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

class RegistrationTests(unittest.TestCase):
    def setUp(self):
        mongo_client.drop_database('backend_test')
        redis_client.flushdb()

        self.start_time = time.clock()
        self.app = test_client
        ## Create test organizer
        data = json.dumps({
            'name': 'Main Organizer',
            'email': 'organizer@gopilot.org',
            'password': 'test-test',
            'type': 'organizer'
        })
        organizer_result = json.loads( self.app.post('/users', headers=h(), data=data).data )
        self.organizer = organizer_result['user']
        self.organizer_token = organizer_result['session']

        data = json.dumps({
            'name': 'Test Event',
            'start_date': str(datetime.datetime.today()+ datetime.timedelta(days=12)),
            'end_date': str(datetime.datetime.today() + datetime.timedelta(days=13)),
            'registration_end': str(datetime.datetime.today() + datetime.timedelta(days=6)),
            'location': 'Tech Inc. HQ',
            'address': '1111 Random Way, Townville, CA'
        })
        self.event = json.loads(self.app.post('/events', headers=h(session=self.organizer_token), data=data).data)['id']

        data = json.dumps({
            'name': 'Test Event',
            'start_date': str(datetime.datetime.today()+ datetime.timedelta(days=5)),
            'end_date': str(datetime.datetime.today() + datetime.timedelta(days=6)),
            'registration_end': str(datetime.datetime.now()),
            'location': 'Tech Inc. HQ',
            'address': '1111 Random Way, Townville, CA'
        });
        self.old_event = json.loads(self.app.post('/events', headers=h(session=self.organizer_token), data=data).data)['id']


        data = json.dumps({
            'name': 'Main Student',
            'email': 'student@gopilot.org',
            'password': 'test-test',
            'type': 'student'
        })
        student_result = json.loads( self.app.post('/users', headers=h(), data=data).data )
        self.student = student_result['user']
        self.student_token = student_result['session']
        self.app.post('/events/'+self.event+'/register', headers=h(session=self.student_token))

        data = json.dumps({
            'name': 'Main Student2',
            'email': 'student2@gopilot.org',
            'password': 'test-test',
            'type': 'student'
        })
        self.student_token2 = json.loads( self.app.post('/users', headers=h(), data=data).data )['session']


        data = json.dumps({
            'name': 'Main Mentor',
            'email': 'mentor@gopilot.org',
            'password': 'test-test',
            'type': 'mentor'
        })
        mentor_result = json.loads( self.app.post('/users', headers=h(), data=data).data )
        self.mentor = mentor_result['user']
        self.mentor_token = mentor_result['session']
        self.app.post('/events/'+self.event+'/register', headers=h(session=self.mentor_token))


    def test_get_attendees(self):
        response = self.app.get('/events/'+self.event+"/attendees", headers=h())
        assert self.mentor['id'] == json.loads(response.data)['mentors'][0]['id']
        assert self.student['id'] == json.loads(response.data)['students'][0]['id']
        assert self.organizer['id'] == json.loads(response.data)['organizers'][0]['id']

    def test_get_organizers(self):
        response = self.app.get('/events/'+self.event+"/organizers", headers=h())
        assert self.organizer['id'] == json.loads(response.data)[0]['id']

    def test_get_mentors(self):
        response = self.app.get('/events/'+self.event+"/mentors", headers=h())
        assert self.mentor['id'] == json.loads(response.data)[0]['id']

    def test_get_students(self):
        response = self.app.get('/events/'+self.event+"/students", headers=h())
        assert self.student['id'] == json.loads(response.data)[0]['id']

    def test_register(self):
        response = self.app.post('/events/'+self.event+"/register", headers=h(session=self.student_token2))
        assert json.loads(response.data)['status'] == "registered"

    def test_register_no_user(self):
        data = json.dumps({
            'user': {
                'name': 'Test Student',
                'email': 'student-tester@gopilot.org'
            }
        })
        response = self.app.post('/events/'+self.event+"/register", headers=h(), data=data)
        assert json.loads(response.data)['status'] == "registered"


    def test_register_old(self):
        response = self.app.post('/events/'+self.old_event+"/register", headers=h(session=self.student_token))
        assert json.loads(response.data)['status'] == "failed"
        assert json.loads(response.data)['reason'] == "closed"

    def test_unregister(self):
        response = self.app.delete('/events/'+self.event+"/register", headers=h(session=self.student_token))
        assert json.loads(response.data)['status'] == "removed"

    def test_user_events(self):
        response = self.app.get('/users/'+self.student['id']+"/events", headers=h())
        assert json.loads(response.data)['upcoming'][0]['id'] == self.event

if __name__ == '__main__':
    unittest.main()
