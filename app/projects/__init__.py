from flask import Flask, Blueprint, request
import app

from dateutil import parser as dateParser
from datetime import datetime

import json
from bson import json_util
import bcrypt

from app.models.users import User, Student, Mentor, Organizer, DeletedUser
from app.models.events import Event
from app.models.projects import Project

projects = Blueprint('projects', __name__)

# POST /projects
@projects.route('', methods=["POST"])
def signup():
    form_name = request.json['name']
    form_event = request.json['event']
    form_creator = request.json['creator']
    
    project = Project()

    project.name = form_name
    project.event = form_event
    project.creators.append( form_creator );

    project.save()

    if not project.id:
        return 'Error creating project', 500
    
    return project.to_json()

# GET /projects
@projects.route('', methods=["GET"])
def get_all():
    user_id = app.auth.check_token( request.headers.get('session') )

    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = User.find_id( user_id )

    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    query = {};

    projects = []
    for project in Project.objects(event=request.json['event'], creators=request.json['creator']):
        projects.append( project.to_json_obj() )

    return json.dumps( projects, default=json_util.default )

# GET /projects/<project_id>
@projects.route('/<project_id>', methods=['GET'])
def find_project(project_id):
    project = Project.find_id( project_id )
    if not project:
        return "Project not found", 404

    return project.to_json()

# PUT /projects/<project_id>
@projects.route('/<project_id>', methods=['PUT'])
def update_project(project_id):
    session_id = app.auth.check_token( request.headers.get('session') )
    if not session_id:
        return "Unauthorized request: Bad session token", 401

    user_sess = User.find_id( session_id )
    if not user_sess:
        return "Session token not found", 404

    if not (session_id == user_id or user_sess.type == "organizer"):
        return "Unauthorized request: You don't have permission for this action", 401

    project = Project.find_id( project_id )
    if not project:
        return "Project not found", 404

    for key, value in request.get_json().items():
        if not key.startswith('_'): # Some security
            setattr(project, key, value)

    project.save()

    return project.to_json()

# DELETE /users/<project_id>
@projects.route('/<project_id>', methods=["DELETE"])
def remove_project(project_id):
    session_id = app.auth.check_token( request.headers.get('session') )
    if not session_id:
        return "Unauthorized request: Bad session token", 401

    user_sess = User.find_id( session_id )
    if not user_sess:
        return "Session token not found", 404

    if not (session_id == user_id or user_sess.type == "organizer"):
        return "Unauthorized request: You don't have permission for this action", 401

    project = Project.find_id( project_id )
    if not project:
        return "Project not found", 404

    deleted_project = DeletedProject( project.id )
    deleted_project.deleted_on = datetime.today()
    deleted_project.save()

    project.remove()
    
    return 'Project deleted'
