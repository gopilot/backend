from flask import Flask, Blueprint
from app import app, db
events = Blueprint('events', __name__)