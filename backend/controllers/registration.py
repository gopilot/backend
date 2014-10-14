from flask import Flask, request

from dateutil import parser as dateParser
from datetime import datetime
from uuid import uuid4 as random_uuid

from backend import EventBlueprint, app, crossdomain
from . import auth

from backend.models import User, Student, Mentor, Organizer, Event, DeletedEvent

import json
import stripe
import sendgrid

jsonType = {'Content-Type': 'application/json'}

## These endpoints need any security?
@EventBlueprint.route('/<event_id>/<attendee_type>', methods=['GET'])
def get_attendees(event_id, attendee_type):
    if not event_id:
        return "Event ID required", 400
    if not Event.find_id( event_id ):
        return "Event not found", 404

    attendee_type = attendee_type.lower()
    if attendee_type not in ['attendees', 'students', 'mentors', 'organizers']:
        return "Invalid Attendee Type", 404

    attendees = None
    if attendee_type == 'attendees':
        attendees = {
            'students': [],
            'mentors': [],
            'organizers': []
        }
        
        for usr in User.objects(events=event_id):
            if usr.type in ['student', 'mentor', 'organizer']:
                attendees[ usr.type+'s' ].append( usr.to_dict() )
            else:
                if not attendees['other']:
                    attendees['other'] = []
                attendees['other'].append( usr.to_dict() )
    else:
        attendees = []
        attendee_cls = None
        if attendee_type == 'students':
            attendee_cls = Student
        elif attendee_type == 'mentors':
            attendee_cls = Mentor
        elif attendee_type == 'organizers':
            attendee_cls = Organizer
        else:
            attendee_cls = User

        
        for usr in attendee_cls.objects(events=event_id):
            attendees.append( usr.to_dict() )

    return json.dumps( attendees ), 200, jsonType

@EventBlueprint.route('/<event_id>/register', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*') # Later, update this to *.gopilot.org
def register(event_id):
    user = None
    sg = sendgrid.SendGridClient('gopilot', app.config["SENDGRID_PASS"])

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    if hasattr(request, 'json') and 'user' in request.json:
        user = Student()
        user.name = request.json['user']['name']
        user.email = request.json['user']['email']
        user.complete = False
        user.completion_token = random_uuid().hex

        if User.objects(email=user.email).first():
            return json.dumps({
                "status": "failed",
                "reason": "email",
                "message": "Your email already has a Pilot account."
            }), 400, jsonType

        if 'stripe_token' in request.json:
            stripe.api_key = app.config['STRIPE_KEY']

            try:
                customer = stripe.Customer.create(
                    card = request.json['stripe_token'],
                    description = user.name,
                    email = user.email
                )
            except stripe.CardError, e:
                print("Customer Card Error", e)
                err = e.json_body['error']
                return json.dumps({
                    "status": "failed",
                    "reason": err['param'] if ('param' in err) else 'customer',
                    "message": err['message']
                }), 400, jsonType
            except:
                return json.dumps({
                    "status": "failed",
                    "reason": "error",
                    "message": "Uh oh, something went wrong..."
                }), 500, jsonType  

            user.stripe_id = customer.id

            try:
                stripe.Charge.create(
                    amount = (event.price * 100), ## Cents
                    currency = "usd",
                    customer = customer.id, 
                    description = "Registration for "+event.name
                )
            except stripe.CardError, e:
                print("Charge Card Error", e)
                err = e.json_body['error']
                return json.dumps({
                    "status": "failed",
                    "reason": err['param'] if ('param' in err) else 'charge',
                    "message": err['message']
                }), 400, jsonType
            except:
                return json.dumps({
                    "status": "failed",
                    "reason": "error",
                    "message": "Uh oh, something went wrong..."
                }), 500, jsonType

        elif event.price > 0:
            return json.dumps({
                "status": "failed",
                "reason": "payment",
                "message": "This event costs $"+event.price+"."
            }), 400, jsonType
    else:
        user_id = auth.check_token( request.headers.get('session') )
        if not user_id:
            return "Unauthorized request: Bad session token", 401

        user = User.find_id( user_id )
        if not user:
            return "Unauthorized request: User doesn't have permission", 401
        if user.type == "organizers":
            return "Organizers can't register for an event", 400

    if(event.registration_end < datetime.now()):
        return json.dumps({
            "status": "failed",
            "reason": "closed",
            "message": "Registration for this event has ended."
        }), 200, jsonType


    
    if event in user.events:
        return json.dumps({
            "status": "failed",
            "reason": "name",
            "message": "You've already registered for this event."
        }), 400, jsonType


    ## Check waitlist, add to event list
    user.events.append( event )
    user.save()
    message = sendgrid.Mail();
    message.add_to(user.name+"<"+user.email+">")
    message.set_from("Pilot <fly@gopilot.org>")
    if user.complete:
        message.set_subject("Your "+event.name+" registration.")
        message.set_html("Thanks for registering!")
        message.set_text("Thanks for registering!")
    else:
        message.set_subject("Complete your "+event.name+" registration")
        message.set_html("Thanks for registering! Click here to finish the process.")
        message.set_text("Thanks for registering! Click here to finish the process.")

    if not app.config['TESTING']:
        status, msg = sg.send(message)
        print(status, msg)
    else:
        print("Sending message", message)

    if user.complete:
        return json.dumps({"status": "registered"}), 200, jsonType
    else:
        return json.dumps({"status": "registered", "token": user.completion_token}), 200, jsonType
    

@EventBlueprint.route('/<event_id>/register', methods=['DELETE'])
def unregister(event_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = User.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_id( event_id )
    if not event:
        return "Event not found", 404

    user.events.remove( event )
    user.save()

    return json.dumps({"status": "removed"}), 200, jsonType


