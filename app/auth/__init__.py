print("top of auth")
from flask import Flask, Blueprint, request, redirect, session
import app
import sys
import json
from uuid import uuid4 as random_uuid
import bcrypt
import types

try:
    from app.models.users import User ## CURRENTLY PRODUCES ERROR
except ImportError:
    print(sys.exc_info())
    print("app", dir(app))
    print('app.models', dir(app.models))
    print('package', app.models.__package__)


print("users imported")
jsonType = {'Content-Type': 'application/json'}

auth = Blueprint('auth', __name__)

# Can be used to ensure that user is logged in. Returns the user_id if the user is logged in, otherwise returns False
def check_token(token):
    # TODO: Make this work
    if not token:
        return False

    user_id = app.sessions.get('session:'+token)
    if not user_id:
        return False
    
    return user_id

def create_token(user_id):
    token = random_uuid().hex
    app.sessions.set('session:'+token, user_id)
    return token

@auth.route('/login', methods=["POST"])
def login():
    form_email = request.get_json().get('email')
    form_password = request.get_json().get('password').encode('utf-8')

    user = User.objects(email=form_email).first()
    if not user or not user.email:
        return 'Email not found', 404

    hashed = user.password.encode('utf-8')

    if bcrypt.hashpw(form_password, hashed) == hashed:
        return json.dumps({
            'session': create_token( user.id ),
            'user': user.to_dict()
        }), 200, jsonType
    else:
        return 'Incorrect password', 401

@auth.route('/check_session', methods=["GET"])
def check_session():
    token = request.headers.get('session')
    if app.sessions.get('session:'+token):
        return "true"
    else:
        return "false"

@auth.route('/retrieve_user', methods=["GET"])
def retrieve_user():
    token = request.headers.get('session')

    user_id = app.sessions.get('session:'+token)
    
    if not user_id:
        return "Session invalid", 401

    user = User.find_id( user_id )
    if not user:
        return "Session invalids", 401

    return user.to_json()
    