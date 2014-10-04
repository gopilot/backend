backend
=======

Backend services for our student/mentor sites

Create a virtualenv for the project, and `pip install -r requirements.txt`.


Running
-------
Running `python setup.py` from the root will run a dev server.

You also must be running mongo and redis (run `mongod` and `redis-server` if the processes aren't running on their own)

Testing
-------
Run `python test.py` to run all tests, or `python -m test.[testFile]` where `testFile` is one of the python scripts in the `test/` directory.


Current Issue with heroku
=========================
For some reason, GUnicorn and heroku are breaking our imports

Before, in auth/__init__.py, I could Import our user model with `import app.models.user`, but when in heroku `app.models` is empty. I've writen a try-catch with some debug info to try to print out what's going on, but at the moment I'm not sure what wrong / how to fix it.

It still works totally fine locally (from both `python setup.py` and `gunicorn`, but on the heroku server the imports break).