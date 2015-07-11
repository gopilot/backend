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

class ScheduleItemTests(unittest.TestCase):
    def setUp(self):
        mongo_client.drop_database('backend_test')
        redis_client.flushdb()

        self.start_time = time.clock()
        self.app = test_client
        ## Create test organizer
        organizer_data = json.dumps({
            'name': 'Main Organizer',
            'email': 'organizer@gopilot.org',
            'password': 'test-test',
            'type': 'organizer'
        })
        self.organizer = json.loads( self.app.post('/users', headers=h(), data=organizer_data).data )
        self.organizer_token = self.organizer['session']
        self.organizer = self.organizer['user']

        student_data = json.dumps({
            'name': 'Test Student',
            'email': 'student@gopilot.org',
            'password': 'test-test',
            'type': 'student'
        })
        self.student = json.loads( self.app.post('/users', headers=h(), data=student_data).data )
        self.student_token = self.student['session']
        self.student = self.student['user']

        event_data = json.dumps({
            'name': 'Test Event',
            'start_date': str(datetime.datetime.today() + datetime.timedelta(days=9)),
            'end_date': str(datetime.datetime.today() + datetime.timedelta(days=10)),
            'registration_end': str(datetime.datetime.today() + datetime.timedelta(days=6)),
            'city': 'San Francisco',
            'slug': 'sf-4',
            'location': 'Tech Inc. HQ',
            'address': '1111 Random Way, Townville, CA'
        })
        self.event = json.loads(self.app.post('/events', headers=h(session=self.organizer_token), data=event_data).data)

        scheduleitem_data = json.dumps({
            'title': 'Test Schedule Item',
            'location': "Some Room",
            'time': '08/15/15 5:00 PM'
        })
        self.scheduleitem = json.loads(self.app.post('/events/'+ self.event['id'] +'/schedule', headers=h(session=self.organizer_token), data=scheduleitem_data).data)

    def test_create_scheduleitem(self):
        data = json.dumps({
            'title': 'Test Schedule Item 2',
            'location': "Some Room",
            'time': '08/14/15 1:00 PM'
        })
        self.app.post('/events/'+ self.event['id'] +'/schedule', headers=h(session=self.organizer_token), data=data)
        data = json.dumps({
            'title': 'Test Schedule Item 3',
            'location': "Some Room",
            'time': '08/15/15 3:00 PM'
        })
        response = self.app.post('/events/'+ self.event['id'] +'/schedule', headers=h(session=self.organizer_token), data=data)
        assert json.loads(response.data)['schedule'][0]['title'] == 'Test Schedule Item 2'
        assert json.loads(response.data)['schedule'][1]['title'] == 'Test Schedule Item 3'
        assert json.loads(response.data)['schedule'][2]['title'] == 'Test Schedule Item'

    def test_update_scheduleitem(self):
        data = json.dumps({
            'title': 'Re-titled Schedule Item'
        })
        response = self.app.put('/events/'+ self.event['id'] +'/schedule/0', headers=h(session=self.organizer_token), data=data)
        assert json.loads(response.data)['schedule'][0]['title'] == 'Re-titled Schedule Item'

    def test_get_all_scheduleitems(self):
        response = self.app.get('/events/'+ self.event['id'] +'/schedule', headers=h(session=self.organizer_token))
        assert len( json.loads(response.data) ) == 1

    def test_get_all_scheduleitem_unauthorized(self):
        response = self.app.get('/events/'+ self.event['id'] +'/schedule', headers=h(session=self.student_token))
        assert response.data == "Unauthorized request: User doesn't have permission"

    def test_delete_scheduleitem(self):
        response = self.app.delete('/events/'+ self.event['id'] +'/schedule/0', headers=h(session=self.organizer_token))
        assert response.data == 'Schedule item deleted'

if __name__ == '__main__':
    unittest.main()
