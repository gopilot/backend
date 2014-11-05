from flask import Flask, request

from dateutil import parser as dateParser
from datetime import datetime

import json
from bson.objectid import ObjectId
import bcrypt

from backend import ProjectBlueprint
from . import auth

from backend.models import User, Student, Mentor, Organizer, DeletedUser, Event, Project


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
        return "Event is required"

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    project.name = request.json.get('name')
    project.event = event
    project.creators = [user];

    description = request.json.get('description')
    if(description):
        project.description = description

    link_github = request.json.get('link_github')
    if(link_github):
        project.link_github = link_github

    link_use = request.json.get('link_use')
    if(link_use):
        project.link_use = link_use

    link_view = request.json.get('link_view')
    if(link_view):
        project.link_view = link_view

    project.save()

    if not project.id:
        return 'Error creating project', 500

    
    return project.to_json()

# GET /projects
@ProjectBlueprint.route('', methods=["GET"])
def get_all():
    projects = []
    query = {}
    for key, obj in request.args.iteritems():
        query[key] = ObjectId(obj)

    for project in Project.objects(**query):
        projects.append( project.to_dict() )

    return json.dumps( projects )

# GET /projects/<event_id>
@ProjectBlueprint.route('/<event_id>', methods=["GET"])
def get_event_projects(event_id):
    projects = []

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    for p in Project.objects(event=event):
        projects.append( p.to_dict() )

    return json.dumps( projects )

# GET /projects/<project_id>
@ProjectBlueprint.route('/<project_id>', methods=['GET'])
def find_project(project_id):
    project = Project.find_id( project_id )
    if not project:
        return "Project not found", 404

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

# GET /projects/<user_id>
@ProjectBlueprint.route('/<event_id>', methods=["GET"])
def get_event_projects(event_id):

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

    if not (user_sess in project.creators or user_sess.type == "organizer"):
        return "Unauthorized request: You don't have permission for this action", 401

    project.delete()
    
    return 'Project deleted'