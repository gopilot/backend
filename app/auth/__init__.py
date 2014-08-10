from flask import Flask, Blueprint, request, redirect, session
import app
import pymongo
from json import dumps
from uuid import uuid4 as random_uuid
import bcrypt
from app.models.users import User, Student, Mentor, Organizer

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
    return token;

@auth.route('/login', methods=["POST"])
def login():
    form_email = request.get_json().get('email')
    form_password = request.get_json().get('password').encode('utf-8')

    user = User.find_one({ 'email': form_email })
    if not user or not user.email:
        return 'Email not found', 404

    hashed = user.password.encode('utf-8')

    if bcrypt.hashpw(form_password, hashed) == hashed:
        return dumps({
            'session': create_token( user._id ),
            'user': user.to_json_obj()
        })
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
    