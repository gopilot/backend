from flask import Flask, request

from dateutil import parser as dateParser
from datetime import datetime

import json
from bson.objectid import ObjectId
import bcrypt

from backend import ProjectBlueprint, EventBlueprint
from . import auth

from backend.models import User, Student, Mentor, Organizer, Event, Project


jsonType = {'Content-Type': 'application/json'}


# POST /projects
@ProjectBlueprint.route('', methods=["POST"])
def create_project():
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = User.find_id( user_id )
    if not user:
        return "User not found", 404
    
    project = Project()


    event_id = request.json.get('event')
    if not event_id:
        return "Event is required", 400
    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404
    if not (event in user.events or event.id in user.events):
        return "User not attending event", 400

    teammate_email = request.json.get('teammate') # A team is required
    if not teammate_email:
        return "Teammate email is required", 400
    teammate = User.objects( email=teammate_email ).first()
    if not teammate:
        return "Teammate not found", 404
    if not (event in teammate.events or event.id in teammate.events):
        return "Teammate not registered for event", 400

    project.name = request.json.get('name')
    project.description = request.json.get('description')
    project.image = request.json.get('image')

    project.event = event
    project.team = []
    project.team.append(user)
    project.team.append(teammate)

    project.save()

    if not project.id:
        return 'Error creating project', 500

    
    return project.select_related(max_depth=1).to_json()

# GET /projects
@ProjectBlueprint.route('', methods=["GET"])
def get_all():
    projects = []
    query = {}
    for key, obj in request.args.iteritems():
        query[key] = ObjectId(obj)

    for project in Project.objects(**query).select_related(max_depth=1):
        projects.append( project.to_dict() )

    return json.dumps( projects ), 200, jsonType

# GET events/<event_id>/projects
@EventBlueprint.route('/<event_id>/projects', methods=['GET'])
def get_event_projects(event_id):
    event = Event.find_event(event_id)
    if not event:
        return "Event not found", 404

    projects = []
    query = {}
    for key, obj in request.args.iteritems():
        query[key] = ObjectId(obj)


    query['name__exists'] = True;
    query['event'] = event.id

    for project in Project.objects(**query).only('name', 'image','description','team', 'prize').select_related(max_depth=1):
        projects.append( project.to_dict() )

    return json.dumps( projects ), 200, jsonType

# GET /projects/<project_id>
@ProjectBlueprint.route('/<project_id>', methods=['GET'])
def find_project(project_id):
    project = Project.find_id( project_id )
    if not project:
        return "Project not found", 404

    return project.to_json()

# POST /projects/<project_id>/addTeammate
@ProjectBlueprint.route('/<project_id>/addTeammate', methods=['POST'])
def add_teammate(project_id):
    project = Project.find_id( project_id )
    if not project:
        return "Project not found", 404

    teammate_email = request.json.get('teammate') # A team is required
    if not teammate_email:
        return "Teammate email is required", 400
    teammate = User.objects( email=teammate_email ).first()
    if not teammate:
        return "Teammate not found", 404
    if not project.event in teammate.events:
        return "Teammate not registered for event", 400

    if len(project.team) >= 5:
        return "Your team is full. Max team size is 5 people.", 400

    project.team.append(teammate)

    project.save()

    return project.select_related(max_depth=1).to_json()

# POST /projects/<project_id>/removeTeammate
@ProjectBlueprint.route('/<project_id>/removeTeammate', methods=['POST'])
def remove_teammate(project_id):
    project = Project.find_id( project_id )
    if not project:
        return "Project not found", 404

    teammate_email = request.json.get('teammate') # A team is required
    if not teammate_email:
        return "Teammate email is required", 400
    teammate = User.objects( email=teammate_email ).first()
    if not teammate:
        teammate = user.find_id(teammate_email)
    if not teammate or not teammate in project.team:
        return "Teammate not found", 404

    project.team.remove(teammate)

    project.save()

    return project.to_json()

# PUT /projects/<project_id>
@ProjectBlueprint.route('/<project_id>', methods=['PUT'])
def update_project(project_id):
    session_id = auth.check_token( request.headers.get('session') )
    if not session_id:
        return "Unauthorized request: Bad session token", 401

    user_sess = User.find_id( session_id )
    if not user_sess:
        return "Session token not found", 404

    project = Project.find_id( project_id )
    if not project:
        return "Project not found", 404

    for key, value in request.get_json().items():
        if not key.startswith('_'): # Some security
            setattr(project, key, value)

    project.save()

    return project.to_json()

# DELETE /users/<project_id>
@ProjectBlueprint.route('/<project_id>', methods=["DELETE"])
def remove_project(project_id):
    session_id = auth.check_token( request.headers.get('session') )
    if not session_id:
        return "Unauthorized request: Bad session token", 401

    user_sess = User.find_id( session_id )
    if not user_sess:
        return "Session token not found", 404

    project = Project.find_id( project_id )
    if not project:
        return "Project not found", 404

    if not (user_sess in project.team or user_sess.type == "organizer"):
        return "Unauthorized request: You don't have permission for this action", 401

    project.delete()
    
    return 'Project deleted'