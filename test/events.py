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

class EventTests(unittest.TestCase):
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
            'start_date': str(datetime.datetime.today()),
            'end_date': str(datetime.datetime.today() + datetime.timedelta(days=1)),
            'location': 'Tech Inc. HQ',
            'address': '1111 Random Way, Townville, CA'
        })
        self.test_event = json.loads(self.app.post('/events', headers=h(session=self.organizer_token), data=data).data)['id']

    def test_create_event(self):
        data = json.dumps({
            'name': 'Test Event',
            'start_date': str(datetime.datetime.today()),
            'end_date': str(datetime.datetime.today() + datetime.timedelta(days=1)),
            'location': 'Tech Inc. HQ',
            'address': '1111 Random Way, Townville, CA',
            'image': 'http://placekitten.com/400/400'
        })
        response = self.app.post('/events', headers=h(session=self.organizer_token), data=data)
        assert len(response.data) > 20

    def test_update_event(self):
        data = json.dumps({
            'name': 'Renamed Event'
        })
        response = self.app.put('/events/'+self.test_event, headers=h(session=self.organizer_token), data=data)
        assert json.loads(response.data)['name'] == 'Renamed Event'

    def test_get_event(self):
        response = self.app.get('/events/'+self.test_event, headers=h(session=self.organizer_token))
        assert json.loads(response.data)['name'] == 'Test Event'

    def test_get_organizers(self):
        response = self.app.get('/events/'+self.test_event+"/organizers", headers=h())
        assert self.organizer['id'] == json.loads(response.data)[0]['id']

    def test_get_attendees(self):
        response = self.app.get('/events/'+self.test_event+"/attendees", headers=h())
        assert len(json.loads(response.data)['students']) >= 0 ## Change this later
        assert len(json.loads(response.data)['mentors']) >= 0
        assert self.organizer['id'] == json.loads(response.data)['organizers'][0]['id']

    def test_get_all_events(self):
        response = self.app.get('/events')
        assert len( json.loads(response.data) ) > 0

    def test_delete_event(self):
        response = self.app.delete('/events/'+self.test_event, headers=h(session=self.organizer_token))
        assert response.data == 'Event deleted'

if __name__ == '__main__':
    unittest.main()