from flask import Flask, request
from dateutil import parser as dateParser
from datetime import datetime
import json
import bcrypt

from backend import UserBlueprint, crossdomain, app
from . import auth

from backend.models import User, Student, Mentor, Organizer, DeletedUser, Event, Project

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
        if app.config['PRODUCTION']:
            return "Error: User doesn't have permission", 401
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

@UserBlueprint.route('/find_incomplete/<token>', methods=['GET'])
@crossdomain(origin='*') # Later, update this to *.gopilot.org
def find_incomplete(token):
    print("line 1", token)
    user = User.objects(completion_token=token)
    print("line 2", user)
    if not user or len(user) < 1: return "Token invalid", 404
    print("line 3")
    return json.dumps({
            'session': auth.create_token( user[0].id ),
            'user': user[0].to_dict()
        }), 200, jsonType

# PUT /users/<user_id>
@UserBlueprint.route('/<user_id>', methods=['PUT', 'OPTIONS'])
@crossdomain(origin='*') # Later, update this to *.gopilot.org
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

    hadError = False;
    for key, value in request.get_json().items():
        if key == "password":
            setattr(user, key, bcrypt.hashpw( value.encode('utf-8'), bcrypt.gensalt() ) )
        elif not key.startswith('_') and not key == "id" and not key=="type" and value != "": # Some security
            setattr(user, key, value)

    if not user.complete and not hadError:   
        user.completion_token = None;
        user.complete = True;

    try:
        user.save()
    except Exception as e:
        print("ERROR SAVING USER OBJECT", str(e))
        print(user.to_dict())
        return json.dumps({
            'error': True,
            'message': "Validation error: "+str(e)
        }), 400, jsonType

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
