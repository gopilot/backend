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

class PostTests(unittest.TestCase):
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

        event_data = json.dumps({
            'name': 'Test Event',
            'start_date': str(datetime.datetime.today() + datetime.timedelta(days=9)),
            'end_date': str(datetime.datetime.today() + datetime.timedelta(days=10)),
            'registration_end': str(datetime.datetime.today() + datetime.timedelta(days=6)),
            'location': 'Tech Inc. HQ',
            'address': '1111 Random Way, Townville, CA'
        })
        self.event = json.loads(self.app.post('/events', headers=h(session=self.organizer_token), data=event_data).data)

        post_data = json.dumps({
            'title': 'Test Post',
            'body': "Some text and other stuff about this post",
            'image': "http://placekitten.com/g/200/200",
            'notif': "Text of the iOS notification"
        })
        self.post = json.loads(self.app.post('/events/'+ self.event['id'] +'/posts', headers=h(session=self.organizer_token), data=post_data).data)

    def test_create_post(self):
        data = json.dumps({
            'title': 'Test Post 2',
            'body': "Some text and other stuff about this second post",
            'image': "http://placekitten.com/g/300/300",
            'notif': "Text of the second iOS notification"
        })
        response = self.app.post('/events/'+ self.event['id'] +'/posts', headers=h(session=self.organizer_token), data=data)

        assert json.loads(response.data)['title'] == 'Test Post 2'
        assert json.loads(response.data)['author']['name'] == 'Main Organizer'
        assert json.loads(response.data)['event']['name'] == "Test Event"

    def test_update_post(self):
        data = json.dumps({
            'title': 'Re-titled Post'
        })
        response = self.app.put('/events/'+ self.event['id'] +'/posts/'+self.post['id'], headers=h(session=self.organizer_token), data=data)
        assert json.loads(response.data)['title'] == 'Re-titled Post'

    def test_get_post(self):
        response = self.app.get('/events/'+ self.event['id'] +'/posts/'+self.post['id'], headers=h(session=self.organizer_token))
        assert json.loads(response.data)['title'] == 'Test Post'

    def test_get_all_posts(self):
        response = self.app.get('/events/'+ self.event['id'] +'/posts', headers=h(session=self.organizer_token))
        assert len( json.loads(response.data) ) == 1

    def test_delete_project(self):
        response = self.app.delete('/events/'+ self.event['id'] +'/posts/'+self.post['id'], headers=h(session=self.organizer_token))
        assert response.data == 'Post deleted'

if __name__ == '__main__':
    unittest.main()
