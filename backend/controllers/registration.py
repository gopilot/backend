from flask import Flask, request, render_template

from dateutil import parser as dateParser
from datetime import datetime
from uuid import uuid4 as random_uuid

from backend import EventBlueprint, app, crossdomain
from . import auth

from backend.models import User, Student, Mentor, Organizer, Event

from backend.controllers.discounts import redeemDiscount, checkDiscount

import json
import bcrypt
import stripe
import sendgrid

jsonType = {'Content-Type': 'application/json'}

## These endpoints need any security?
@EventBlueprint.route('/<event_id>/<attendee_type>', methods=['GET'])
def get_attendees(event_id, attendee_type):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401
    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    if not event_id:
        return "Event ID required", 400
    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    attendee_type = attendee_type.lower()
    if attendee_type not in ['attendees', 'students', 'mentors', 'organizers']:
        return "Invalid Attendee Type", 404

    attendees = None
    if attendee_type == 'attendees':
        attendees = {
            'students': [],
            'mentors': [],
            'organizers': [],
            'checkins': []
        }
        
        for usr in User.objects(events=event.id) :
            if usr.type in ['student', 'mentor', 'organizer']:
                attendees[ usr.type+'s' ].append( usr.to_dict() )
            else:
                if not attendees['other']:
                    attendees['other'] = []
                attendees['other'].append( usr.to_dict() )

        for usr in User.objects(checkins=event.id):
            attendees[ 'checkins' ].append( usr.to_dict() )

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

        
        for usr in attendee_cls.objects(events=event.id):
            attendees.append( usr.to_dict() )

    return json.dumps( attendees ), 200, jsonType

@EventBlueprint.route('/<event_id>/register/mentor', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*') # Later, update this to *.gopilot.org
def register_mentor(event_id):
    sg = sendgrid.SendGridClient('gopilot', app.config["SENDGRID_PASS"])

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    user = Mentor()

    for key, value in request.get_json().items():
        if key == "password":
            setattr(user, key, bcrypt.hashpw( value.encode('utf-8'), bcrypt.gensalt() ) )
        elif not key.startswith('_') and not key == "id": # Some security
            setattr(user, key, value)

    user.events.append( event )
    user.save()

    message = sendgrid.Mail();
    message.add_to(user.name+"<"+user.email+">")
    message.set_from("Pilot <fly@gopilot.org>")
    message.set_subject("Thanks for signing up to mentor at "+event.name+"!")
    email_html = render_template('mentor_registration.html',
        event_name=event.name,
        first_name=user.name.split(' ')[0], 
        subject="Thanks for signing up to mentor at for "+event.name+"!"
    )
    message.set_html(email_html)
    email_text = render_template('mentor_registration.txt',
        event_name=event.name,
        first_name=user.name.split(' ')[0], 
        subject="Thanks for signing up to mentor at "+event.name+"!"
    )
    message.set_text(email_text)

    if not app.config['TESTING']:
        status, msg = sg.send(message)
        print(status, msg)
    else:
        print("Sending message to "+user.email, message)

    return user.to_json()


@EventBlueprint.route('/<event_id>/register', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*') # Later, update this to *.gopilot.org
def register(event_id):
    user = None
    discount = False
    sg = sendgrid.SendGridClient('gopilot', app.config["SENDGRID_PASS"])

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    price = event.price

    if hasattr(request, 'json') and request.json and 'user' in request.json:
        if User.objects(email=request.json['user']['email']).first():
            return json.dumps({
                "status": "failed",
                "reason": "email",
                "message": "Your email already has a Pilot account."
            }), 400, jsonType
        
        print("has user")
        user = Student()
        user.name = request.json['user']['name']
        user.email = request.json['user']['email']
        user.complete = False
        user.completion_token = random_uuid().hex


        if 'discount' in request.json and request.json['discount'] != False:
            print("has discount")
            # user.save()
            discount = checkDiscount(request.json['discount'])
            if discount:
                price -= discount

        print("Charging user %s" % price)
        if 'stripe_token' in request.json:
            print("has stripe")
            stripe.api_key = app.config['STRIPE_KEY']

            try:
                customer = stripe.Customer.create(
                    source = request.json['stripe_token'],
                    description = user.name,
                    email = user.email
                )
            except stripe.CardError, e:
                app.logger.error("Customer Card Error: "+str(e))
                err = e.json_body['error']
                return json.dumps({
                    "status": "failed",
                    "reason": err['param'] if ('param' in err) else 'customer',
                    "message": err['message']
                }), 400, jsonType

            user.stripe_id = customer.id
            try:
                stripe.Charge.create(
                    amount = (price * 100), ## Cents
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

        elif price > 0:
            print("price > 0")
            return json.dumps({
                "status": "failed",
                "reason": "payment",
                "message": "This event costs $%s." % price
            }), 400, jsonType
    else:
        print("user account exists")
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
    print("user saving event")
    user.events.append( event )

    user.save()

    if discount:
        print("redeeming discount")
        redeemDiscount(user, event, request.json['discount'])

    message = sendgrid.Mail();
    message.add_to(user.name+"<"+user.email+">")
    message.set_from("Pilot <fly@gopilot.org>")

    message.set_subject("Your "+event.name+" registration.")
    email_html = render_template('registration.html',
        event_name=event.name,
        first_name=user.name.split(' ')[0], 
        subject="Your "+event.name+" registration."
    )
    message.set_html(email_html)
    email_text = render_template('registration.txt',
        event_name=event.name,
        first_name=user.name.split(' ')[0], 
        subject="Your "+event.name+" registration."
    )
    message.set_text(email_text)

    if not app.config['TESTING']:
        status, msg = sg.send(message)
        print(status, msg)
    else:
        print("Sending message", message)

    if not user.events:
        print("USER MISSING EVENTS")
        print(user.to_dict())
        user.events.append( event )
        user.save()
        print("saved user")
    result = user.save()
    print(user.to_dict())
    print("SAVE RESULT", result)

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

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404
    if event in user.events:
        user.events.remove( event )
    user.save()

    return json.dumps({"status": "removed"}), 200, jsonType

@EventBlueprint.route('/<event_id>/checkin', methods=['POST'])
def checkin(event_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    attendee = User.find_id( request.json['attendee_id'] )
    if not attendee:
        return "Attendee not found", 404

    if not event in attendee.events:
        return "Attendee not registered", 401

    attendee.checkins.append( event )
    attendee.save()

    return json.dumps({"status": "success"}), 200, jsonType

@EventBlueprint.route('/<event_id>/checkin', methods=['DELETE'])
def checkout(event_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return "Unauthorized request: Bad session token", 401

    user = Organizer.find_id( user_id )
    if not user:
        return "Unauthorized request: User doesn't have permission", 401

    event = Event.find_event( event_id )
    if not event:
        return "Event not found", 404

    attendee = User.find_id( request.json['attendee_id'] )
    if not attendee:
        return "Attendee not found", 404

    if event in attendee.checkins:
        attendee.checkins.remove( event )
    attendee.save()

    return json.dumps({"status": "removed"}), 200, jsonType


