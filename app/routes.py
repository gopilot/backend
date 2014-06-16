from flask import Flask, render_template, request, redirect
from app import app

from controllers import users, events, auth

@app.route('/')
def hello_world():
	user = auth.ensure_login();
	if not user:
		return 'Not currently logged in. <br> <a href="/login">Login</a> | <a href="/signup">Signup</a>'
	else:
		return 'Hello, '+user['name']+'! <br> <a href="/logout">Logout</a>'

@app.route('/index', methods=['GET'])
def index():
	return render_template('index.html')


# Auth Routes
@app.route('/login', methods=['GET'])
def login_page():
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
	return auth.login()

@app.route('/signup', methods=['GET'])
def signup_page():
	return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
	return auth.signup()

@app.route('/logout', methods=['GET'])
def logout():
	return auth.logout()