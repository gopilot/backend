from flask import Flask, request
from dateutil import parser as dateParser
from datetime import datetime
import json
import bcrypt

from backend import UserBlueprint
from . import auth

from backend.models.users import User, Student, Mentor, Organizer, DeletedUser
from backend.models.events import Event
from backend.models.projects import Project

jsonType = {'Content-Type': 'application/json'}

# POST /users
@UserBlueprint.route('', methods=["POST"])
def signup():
    form_name = request.json['name']
    form_email = request.json['email']
    form_password = request.json['password']
    form_type = request.json['type'] # student or mentor

    if len(form_password) < 8:
        return 'Password must be 8 characters or longer', 400

    if User.objects(email=form_email).first():
        return 'Email already exists', 400

    user = User()

    if form_type == 'student':
        user = Student()
    elif form_type == 'mentor':
        user = Mentor()
    elif form_type == 'organizer':
        user = Organizer()

    user.name = form_name
    user.email = form_email
    user.password = bcrypt.hashpw( form_password.encode('utf-8'), bcrypt.gensalt() )

    user.save()

    if not user.id:
        return 'Error creating account', 500
    
    return json.dumps({
            'session': auth.create_token( user.id ),
            'user': user.to_dict()
        }), 200, jsonType

# GET /users
@UserBlueprint.route('', methods=["GET"])
def get_all():
    user_id = auth.check_token( request.headers.get('session') )

    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )

    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    users = []
    for usr in User.objects:
        users.append( usr.to_dict() )

    return json.dumps( users ), 200, jsonType

# GET /users/<user_id>
@UserBlueprint.route('/<user_id>', methods=['GET'])
def find_user(user_id):
    user = User.find_id( user_id )
    if not user:
        return "User not found", 404

    return user.to_json()

# PUT /users/<user_id>
@UserBlueprint.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    session_id = auth.check_token( request.headers.get('session') )
    if not session_id:
        return "Unauthorized request: Bad session token", 401

    user_sess = User.find_id( session_id )
    if not user_sess:
        return "Session token not found", 404

    if (not session_id == user_id) and (not user_sess.type == "organizer"):
            return "Unauthorized request: You don't have permission for this action", 401

    user = User.find_id( user_id )
    if not user:
        return "User not found", 404

    for key, value in request.get_json().items():
        if not key.startswith('_'): # Some security
            setattr(user, key, value)

    user.save()

    return user.to_json()

# DELETE /users/<user_id>
@UserBlueprint.route('/<user_id>', methods=["DELETE"])
def remove_user(user_id):
    session_id = auth.check_token( request.headers.get('session') )
    if not session_id:
        return "Unauthorized request: Bad session token", 401

    user_sess = User.find_id( session_id )
    if not user_sess:
        return "Session token not found", 404

    if (not session_id == user_id) and (not user_sess.type == "organizer"):
            return "Unauthorized request: You don't have permission for this action", 401

    user = User.find_id( user_id )
    if not user:
        return "User not found", 404
    deleted_user = DeletedUser( **user._data )
    deleted_user.deleted_on = datetime.today()
    deleted_user.save()

    user.delete()
    
    return 'User deleted'

# GET /users/<user_id>
@UserBlueprint.route('/<user_id>/events', methods=['GET'])
def find_user_events(user_id):
    user = User.find_id( user_id )
    if not user:
        return "User not found", 404

    result = {
        "upcoming": [],
        "attended": []
    }
    for evt in user.events:
        if evt.start_date > datetime.now():
            result['upcoming'].append( evt.to_dict() )
        else:
            result['attended'].append( evt.to_dict() )

    return json.dumps( result ), 200, jsonType