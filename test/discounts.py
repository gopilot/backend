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

class DiscountTests(unittest.TestCase):
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
            'slug': 'sf-3',
            'location': 'Tech Inc. HQ',
            'address': '1111 Random Way, Townville, CA'
        })
        self.event = json.loads(self.app.post('/events', headers=h(session=self.organizer_token), data=event_data).data)

        discount_data = json.dumps({
            'title': 'Test Discount',
            'amount': 10,
            'code': "skdjfoejsk"
        })
        self.discount = json.loads(self.app.post('/events/'+ self.event['id'] +'/discounts', headers=h(session=self.organizer_token), data=discount_data).data)

    def test_create_discount(self):
        data = json.dumps({
            'title': 'Test Discount 2',
            'amount': 15,
            'code': "stsdjfdsdf"
        })
        response = self.app.post('/events/'+ self.event['id'] +'/discounts', headers=h(session=self.organizer_token), data=data)

        assert json.loads(response.data)['title'] == 'Test Discount 2'
        assert json.loads(response.data)['amount'] == 15
        assert json.loads(response.data)['event']['name'] == "Test Event"

    def test_update_discount(self):
        data = json.dumps({
            'title': 'Re-titled Discount',
            'amount': 5
        })
        response = self.app.put('/events/'+ self.event['id'] +'/discounts/'+self.discount['id'], headers=h(session=self.organizer_token), data=data)
        assert json.loads(response.data)['amount'] == 5

    def test_get_discount(self):
        response = self.app.get('/events/'+ self.event['id'] +'/discounts/'+self.discount['code'], headers=h(session=self.organizer_token))
        assert json.loads(response.data)['title'] == 'Test Discount'

    def test_get_all_discounts(self):
        response = self.app.get('/events/'+ self.event['id'] +'/discounts', headers=h(session=self.organizer_token))
        assert len( json.loads(response.data) ) == 1

    def test_get_all_discounts_unauthorized(self):
        response = self.app.get('/events/'+ self.event['id'] +'/discounts', headers=h(session=self.student_token))
        assert json.loads(response.data)['message'] == "Unauthorized request: User doesn't have permission"

    def test_delete_discount(self):
        response = self.app.delete('/events/'+ self.event['id'] +'/discounts/'+self.discount['id'], headers=h(session=self.organizer_token))
        assert response.data == 'Discount deleted'

if __name__ == '__main__':
    unittest.main()
