from flask import Flask, request, redirect, session
import sys
import json
from uuid import uuid4 as random_uuid
import bcrypt

from backend import sessions, AuthBlueprint

from backend.models import User

jsonType = {'Content-Type': 'application/json'}


# Can be used to ensure that user is logged in. Returns the user_id if the user is logged in, otherwise returns False
def check_token(token):
    # TODO: Make this work
    if not token:
        return False

    user_id = sessions.get('session:'+token)
    if not user_id:
        return False
    
    return user_id

def create_token(user_id):
    print("creating token...")
    token = random_uuid().hex
    print("found random")
    sessions.set('session:'+token, user_id)
    print("set session")
    return token

@AuthBlueprint.route('/login', methods=["POST"])
def login():
    form_email = request.get_json().get('email')
    form_password = request.get_json().get('password').encode('utf-8')

    user = User.objects(email=form_email).first()
    if not user or not user.email:
        return 'Email not found', 404
    print("found user")
    hashed = user.password.encode('utf-8')
    print("hashed pw")
    if bcrypt.hashpw(form_password, hashed) == hashed:
        print("Correct password")
        sessionToken = create_token( user.id )
        print('created token')
        userdict = user.to_dict()
        print('created userdict')
        sendInfo = {
            'session': sessionToken,
            'user': userdict
        }
        jsonInfo = json.dumps(sendInfo)
        print("json dumped, sending...")
        return jsonInfo, 200, jsonType
    else:
        print("failure")
        return 'Incorrect password', 401

@AuthBlueprint.route('/check_session', methods=["GET"])
def check_session():
    token = request.headers.get('session')
    if sessions.get('session:'+token):
        return "true"
    else:
        return "false"

@AuthBlueprint.route('/retrieve_user', methods=["GET"])
def retrieve_user():
    token = request.headers.get('session')

    user_id = sessions.get('session:'+token)
    
    if not user_id:
        return "Session invalid", 401

    user = User.find_id( user_id )
    if not user:
        return "Session invalids", 401

    return user.to_json()
    