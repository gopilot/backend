from flask import Flask, Blueprint
from app import app
users = Blueprint('users', __name__)