from flask import Flask, request, redirect, session
import sys
import json
from uuid import uuid4 as random_string
import bcrypt

from backend import sessions, AuthBlueprint, app

from backend.models import User

from azure.storage import BlobService, AccessPolicy, SharedAccessPolicy, BlobSharedAccessPermissions

import datetime


azure_storage = BlobService(app.config['AZURE_NAME'], app.config['AZURE_KEY'])



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
    token = random_string().hex
    sessions.set('session:'+token, user_id)
    return token

def create_filename():
    return str(random_string().bytes.encode('base64').rstrip('=\n').replace('/', '_'))

@AuthBlueprint.route('/login', methods=["POST"])
def login():
    form_email = request.get_json().get('email')
    form_password = request.get_json().get('password')

    user = User.objects(email=form_email).first()
    if not user or not user.email:
        return 'Email not found', 404
    hashed = user.password.encode('utf-8')
    if bcrypt.hashpw(form_password.encode('utf-8'), hashed) == hashed:
        return json.dumps({
            'session': create_token( user.id ),
            'user': user.to_dict()
        }), 200, jsonType
    else:
        return 'Incorrect password', 401

@AuthBlueprint.route('/logout', methods=["POST"])
def logout():
    token = request.headers.get('session')
    sessions.delete('session:'+token);

    return json.dumps({
        'status': 'success'
    }), 200, jsonType

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
        return "Session invalid", 401

    return user.to_json()

@AuthBlueprint.route('/request_upload/<upload_location>', methods=["GET"])
def request_upload(upload_location):
    filetype = request.args.get("filetype")
    filesize = request.args.get("filesize")

    if filetype not in ['png', 'jpg', 'jpeg', 'gif', 'pdf']:
        return "Invalid filetype", 400

    # TODO: Check filesize

    if upload_location not in ["event", "user", "project"]:
        return "Invalid upload location", 400

    token = request.headers.get('session')

    user_id = sessions.get('session:'+token)
    
    if not user_id:
        return "Session invalid", 40

    user = User.find_id( user_id )
    if not user:
        return "Session invalid", 401

    if upload_location == "event" and user.type != "organizer":
        return "You don't have permission to upload", 401;
    

    upload_policy = SharedAccessPolicy(AccessPolicy(
        expiry= str(datetime.datetime.now() + datetime.timedelta(minutes=10)),
        permission=BlobSharedAccessPermissions.WRITE,
    ))
    destination_url = upload_location+"/"+create_filename()+'.'+filetype

    # TODO: fix "Incorrect Padding" exception on this line
    upload_token = azure_storage.generate_shared_access_signature(
        container_name='user-files',
        blob_name= destination_url,
        shared_access_policy=upload_policy,
    )
    print("Created Destination Url "+destination_url)
    print("Created upload url "+upload_token.url())
    return json.dumps({
            "upload_url": upload_token.url(),
            "file_url": "https://files.gopilot.org/user-files/"+destination_url
        }), 200, jsonType

    