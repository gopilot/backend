backend
=======

Backend services for our student/mentor sites

Create a virtualenv for the project, and `pip install -r requirements.txt`.

This branch is a (currently non-working) port to Python 3. 

Running
-------
Running `python setup.py` from the root will run a dev server.

You also must be running mongo and redis (run `mongod` and `redis-server` if the processes aren't running on their own)

Testing
-------
Run `python test.py` to run all tests, or `python -m test.[testFile]` where `testFile` is one of the python scripts in the `test/` directory.

Known Issues
============
- Line 20 of document.py is currently broken in python3, because ObjectId() isn't parsing the string correectly.