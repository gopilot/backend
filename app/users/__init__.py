from flask import Flask, Blueprint
import app

from dateutil import parser as dateParser
from datetime import datetime

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

users = Blueprint('users', __name__)

# POST /users
@users.route('', methods=["POST"])
def signup():
    form_name = request.json['name']
    form_email = request.json['email']
    form_password = request.json['password']
    form_type = request.json['type'] # student or mentor

    if len(form_password) < 8:
        return 'Password must be 8 characters or longer', 400

    if User.find_one({ 'email': form_email }):
        return 'Email already exists', 400

    user = User()

    if form_type == 'student':
        user = Student()
    elif form_type == 'mentor':
        user = Mentor()
    elif form_type == 'organizer':
        user = Organizer()

    user.type = form_type
    user.name = form_name
    user.email = form_email
    user.password = bcrypt.hashpw( form_password.encode('utf-8'), bcrypt.gensalt() )

    user_id = user.save()

    if not user_id:
        return 'Error creating account', 500
    
    return app.auth.create_token( user_id )

# GET /users
@users.route('', methods=["GET"])
def get_all():
    user_id = app.auth.check_token( request.headers.get('session') )

    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )

    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    users = []
    for usr in User.find():

        if(usr.type == "student"):
            usr = Student( id=usr._id )
        elif(usr.type == "mentor"):
            usr = Mentor( id=usr._id )
        elif(usr.type == "organizer"):
            usr = Organizer( id=usr._id )

        users.append( usr.to_json_obj() )
    return json.dumps( users, default=json_util.default )

# GET /users/<user_id>
@users.route('/<user_id>', methods=['GET'])
def find_user(user_id):
    user = User.find_id( user_id )
    if not user:
        return "User not found", 404

    if(user.type == "student"):
        user = Student( id=user._id )
    elif(user.type == "mentor"):
        user = Mentor( id=user._id )
    elif(user.type == "organizer"):
        user = Organizer( id=user._id )

    return user.to_json()

# PUT /users/<user_id>
@users.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    session_id = app.auth.check_token( request.headers.get('session') )
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

    if(user.type == "student"):
        user = Student( id=user._id )
    elif(user.type == "mentor"):
        user = Mentor( id=user._id )
    elif(user.type == "organizer"):
        user = Organizer( id=user._id )

    for key, value in request.get_json().items():
        if not key.startswith('_'): # Some security
            setattr(user, key, value)

    user.save()

    return user.to_json()

# DELETE /users/<user_id>
@users.route('/<user_id>', methods=["DELETE"])
def remove_user(user_id):
    session_id = app.auth.check_token( request.headers.get('session') )
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

    deleted_user = DeletedUser( id=user._id, from_collection="users" )
    deleted_user.deleted_on = datetime.today()
    deleted_user.save()

    user.remove()
    
    return 'User deleted'
