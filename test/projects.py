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

class ProjectTests(unittest.TestCase):
    def setUp(self):
        mongo_client.drop_database('backend_test')
        redis_client.flushdb()

        self.start_time = time.clock()
        self.app = test_client
        ## Create test organizer
        student_data = json.dumps({
            'name': 'Main Student',
            'email': 'student@gopilot.org',
            'password': 'test-test',
            'type': 'student'
        })
        self.student = json.loads( self.app.post('/users', headers=h(), data=student_data).data )
        self.student_token = self.student['session']
        self.student = self.student['user']

        teammate_data = json.dumps({
            'name': "Student's Friend",
            'email': 'teammate@gopilot.org',
            'password': 'test-test',
            'type': 'student'
        })
        self.teammate = json.loads( self.app.post('/users', headers=h(), data=teammate_data).data )
        self.teammate_token = self.teammate['session']
        self.teammate = self.teammate['user']

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
            'city': 'San Francisco',
            'slug': 'sf-5',
            'location': 'Tech Inc. HQ',
            'address': '1111 Random Way, Townville, CA'
        })
        self.event = json.loads(self.app.post('/events', headers=h(session=self.organizer_token), data=event_data).data)

        project_data = json.dumps({
            'name': 'Test Project',
            'event': self.event['id'],
            'teammate': self.teammate['email']
        })
        self.project = json.loads(self.app.post('/projects', headers=h(session=self.student_token), data=project_data).data)

    def test_create_project(self):
        data = json.dumps({
            'name': 'Test Project2',
            'event': self.event['id'],
            'teammate': self.teammate['email']
        })
        response = self.app.post('/projects', headers=h(session=self.student_token), data=data)

        assert json.loads(response.data)['name'] == 'Test Project2'
        assert json.loads(response.data)['team'][0]['name'] == 'Main Student'
        assert json.loads(response.data)['event']['name'] == "Test Event"

    def test_update_project(self):
        data = json.dumps({
            'name': 'Renamed Project'
        })
        response = self.app.put('/projects/'+self.project['id'], headers=h(session=self.student_token), data=data)
        assert json.loads(response.data)['name'] == 'Renamed Project'

    def test_update_project_organizer(self):
        data = json.dumps({
            'name': 'Renamed Project2'
        })
        response = self.app.put('/projects/'+self.project['id'], headers=h(session=self.organizer_token), data=data)
        assert json.loads(response.data)['name'] == 'Renamed Project2'

    def test_get_project(self):
        response = self.app.get('/projects/'+self.project['id'], headers=h(session=self.student_token))
        assert json.loads(response.data)['name'] == 'Test Project'

    def test_get_all_projects(self):
        response = self.app.get('/projects')
        assert len( json.loads(response.data) ) == 1

    def test_get_all_projects_query(self):
        event2_data = json.dumps({
            'name': 'Test Event 2',
            'start_date': str(datetime.datetime.today() + datetime.timedelta(days=9)),
            'end_date': str(datetime.datetime.today() + datetime.timedelta(days=10)),
            'registration_end': str(datetime.datetime.today() + datetime.timedelta(days=6)),
            'city': 'San Francisco',
            'slug': 'sf-9',
            'location': 'Tech Inc. HQ',
            'address': '1111 Random Way, Townville, CA'
        })
        self.event2 = json.loads(self.app.post('/events', headers=h(session=self.organizer_token), data=event2_data).data)

        project2_data = json.dumps({
            'name': 'Test Project',
            'event': self.event2['id'],
            'teammate': self.teammate['email']
        })
        self.app.post('/projects', headers=h(session=self.student_token), data=project2_data)

        response = self.app.get('/projects?event='+self.event['id'])

        assert len( json.loads(response.data) ) == 1

    def test_get_all_projects_event(self):
        event2_data = json.dumps({
            'name': 'Test Event 2',
            'start_date': str(datetime.datetime.today() + datetime.timedelta(days=9)),
            'end_date': str(datetime.datetime.today() + datetime.timedelta(days=10)),
            'registration_end': str(datetime.datetime.today() + datetime.timedelta(days=6)),
            'city': 'San Francisco',
            'slug': 'sf-9',
            'location': 'Tech Inc. HQ',
            'address': '1111 Random Way, Townville, CA'
        })
        self.event2 = json.loads(self.app.post('/events', headers=h(session=self.organizer_token), data=event2_data).data)

        project2_data = json.dumps({
            'name': 'Test Project',
            'event': self.event2['id'],
            'teammate': self.teammate['email']
        })
        self.app.post('/projects', headers=h(session=self.student_token), data=project2_data)

        response = self.app.get('/events/'+self.event2['id']+'/projects')

        assert len( json.loads(response.data) ) == 1

    def test_get_all_projects_creator(self):
        student_data = json.dumps({
            'name': 'Main Student 2',
            'email': 'student2@gopilot.org',
            'password': 'test-test',
            'type': 'student'
        })
        self.student2_token = json.loads(self.app.post('/users', headers=h(), data=student_data).data )['session']


        project2_data = json.dumps({
            'name': 'Test Project',
            'event': self.event['id'],
            'teammate': self.teammate['email']
        })
        self.app.post('/projects', headers=h(session=self.student2_token), data=project2_data)

        response = self.app.get('/projects?team='+self.student['id'])

        assert len( json.loads(response.data) ) == 1

    def test_delete_project(self):
        response = self.app.delete('/projects/'+self.project['id'], headers=h(session=self.student_token))
        assert response.data == 'Project deleted'

    def test_delete_project_organizer(self):
        response = self.app.delete('/projects/'+self.project['id'], headers=h(session=self.organizer_token))
        assert response.data == 'Project deleted'


if __name__ == '__main__':
    unittest.main()
