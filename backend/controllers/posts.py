from flask import Flask, request

from dateutil import parser as dateParser
from datetime import datetime

from backend import EventBlueprint
from . import auth

from backend.models import User, Student, Mentor, Organizer, Event, Post

import json
jsonType = {'Content-Type': 'application/json'}

# POST /posts
@EventBlueprint.route('/<event_id>/posts', methods=['POST'])
def create_post(event_id):
    user_id = auth.check_token( request.headers.get('session') )

    if not user_id:
        return "Unauthorized request: Bad session token", 401

    organizer = Organizer.find_id( user_id )
    if not organizer:
        return "Unauthorized request: User doesn't have permission", 401


    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    body = request.get_json()
    post = Post()
    post.event = event
    post.author = organizer

    post.image = body.get('image')
    post.title = body.get('title')
    post.body = body.get('body')

    if body.get('notif'):
        post.notif = body.get('notif')
    else:
        post.notif = post.title
    print("Saving post", post)
    post.save()
    print("Post saved, id", post.id)

    if not post.id:
        return "Error creating post", 500

    # Send push notification through Amazon SNS?

    return post.to_json()

# GET /posts
@EventBlueprint.route('/<event_id>/posts', methods=['GET'])
def all_posts(event_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = User.find_id( user_id )
    if not user:
        return "User not found", 404

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    attended_ids = [ evt.id for evt in user.events ]

    if not (event.id in attended_ids or user.type == "organizer"):
        return "Unauthorized request: User doesn't have permission"

    posts = []
    for p in Post.objects(event=event):
        posts.append( p.to_dict() )

    return json.dumps( posts ), 200, jsonType

# GET /posts/<post_id>
@EventBlueprint.route('/<event_id>/posts/<post_id>', methods=['GET'])
def get_post(event_id, post_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = User.find_id( user_id )
    if not user:
        return "User not found", 404

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    attended_ids = [ evt.id for evt in user.events ]

    if not (event.id in attended_ids or user.type == "organizer"):
        return "Unauthorized request: User doesn't have permission"

    post = Post.find_id( post_id )
    if not post:
        return "Post not found", 404

    return post.to_json()

# PUT /posts/<post_id>
@EventBlueprint.route('/<event_id>/posts/<post_id>', methods=['PUT'])
def update_post(event_id, post_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    post = Post.find_id( post_id )
    if not post:
        return "Post not found", 404

    for key, value in request.get_json().items():
        if not key.startswith('_'): # Some security
            setattr(post, key, value)

    post.save()

    return post.to_json()

# DELETE /posts/<post_id>
@EventBlueprint.route('/<event_id>/posts/<post_id>', methods=["DELETE"])
def delete_post(event_id, post_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    post = Post.find_id( post_id )
    if not post:
        return "Post not found", 404

    post.delete()
    
    return 'Post deleted'