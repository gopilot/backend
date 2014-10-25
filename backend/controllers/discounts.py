from flask import Flask, request

from dateutil import parser as dateParser
from datetime import datetime

from backend import EventBlueprint, crossdomain, send_error
from . import auth

from backend.models import User, Student, Mentor, Organizer, Event, Discount

import json
jsonType = {'Content-Type': 'application/json'}

def redeemDiscount(user, discount_code):
    discount = Discount.objects(code=discount_code)[0]
    if not (discount and discount.active):
        return False

    discount.claimed.append( user )

    if discount.limit and len(discount.claimed) == discount.limit:
        discount.active = False

    discount.save()
    
    return discount.amount


# POST /discounts
@EventBlueprint.route('/<event_id>/discounts', methods=['POST'])
def create_discount(event_id):
    user_id = auth.check_token( request.headers.get('session') )

    if not user_id:
        return send_error("Unauthorized request: Bad session token", 401)

    organizer = Organizer.find_id( user_id )
    if not organizer:
        return send_error("Unauthorized request: User doesn't have permission", 401)


    event = Event.find_id( event_id )
    if not event:
        return send_error("Event not found", 404)

    body = request.get_json()

    if Discount.objects(code=body.get('code')):
        return send_error("Code already exists", 400)

    discount = Discount()
    discount.event = event

    discount.title = body.get('title')
    discount.amount = body.get('amount')
    discount.code = body.get('code')

    if body.get('limit'):
        discount.limit = body.get('limit')

    discount.save()

    if not discount.id:
        return send_error("Error creating discount", 500)

    return discount.to_json()

# GET /discounts
@EventBlueprint.route('/<event_id>/discounts', methods=['GET'])
def all_discounts(event_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return send_error("Unauthorized request: Bad session token", 401)

    user = Organizer.find_id( user_id )
    if not user or user.type != "organizer":
        return send_error("Unauthorized request: User doesn't have permission", 404)

    event = Event.find_id( event_id )
    if not event:
        return send_error("Event not found", 404)

    discounts = []
    for d in Discount.objects(event=event):
        discounts.append( d.to_dict() )

    return json.dumps( discounts ), 200, jsonType

# GET /discounts/<discount_code>
@EventBlueprint.route('/<event_id>/discounts/<discount_code>', methods=['GET'])
def get_discount(event_id, discount_code):
    event = Event.find_id( event_id )
    if not event:
        return send_error("Event not found", 404)

    discount = Discount.find_id( discount_code )
    if not discount:
        discount = Discount.objects(code=discount_code)[0]
    
    if not discount:
        return send_error("Discount not found", 404)

    return discount.to_json()

# PUT /discounts/<discount_id>
@EventBlueprint.route('/<event_id>/discounts/<discount_id>', methods=['PUT'])
def update_discount(event_id, discount_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return send_error("Unauthorized request: Bad session token", 401)

    user = Organizer.find_id( user_id )
    if not user or user.type != "organizer":
        return send_error("Unauthorized request: User doesn't have permission", 401)

    event = Event.find_id( event_id )
    if not event:
        return send_error("Event not found", 404)

    discount = Discount.find_id( discount_id )
    if not discount:
        return send_error("Discount not found", 404)

    for key, value in request.get_json().items():
        if not key.startswith('_'): # Some security
            setattr(discount, key, value)

    discount.save()

    return discount.to_json()

# DELETE /discounts/<discount_id>
@EventBlueprint.route('/<event_id>/discounts/<discount_id>', methods=["DELETE"])
def delete_discount(event_id, discount_id):
    user_id = auth.check_token( request.headers.get('session') )
    if not user_id:
        return send_error("Unauthorized request: Bad session token", 401)

    user = Organizer.find_id( user_id )
    if not user:
        return send_error("Unauthorized request: User doesn't have permission", 401)

    event = Event.find_id( event_id )
    if not event:
        return send_error("Event not found", 404)

    discount = Discount.find_id( discount_id )
    if not discount:
        return send_error("Discount not found", 404)

    discount.delete()
    
    return 'Discount deleted'