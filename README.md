backend
=======

Backend services for our student/mentor sites

Create a virtualenv for the project, and `pip install -r requirements.txt`.

Running `python setup.py` from the root will run a dev server.

You also must be running mongo (run `mongod` if the process isn't running on its own)


Weird bug (7/26/14)
-------------------

For some reason, saving ORM objects isn't working in our routes. If you look at [line #109](https://github.com/gopilot/backend/blob/bee4d092d01f282a8921e8aacf90a566f32328f6/app/auth/__init__.py#L109) of the auth routes, each one of those value assignments isn't calling the [\_\_set\_\_() method](https://github.com/gopilot/backend/blob/bee4d092d01f282a8921e8aacf90a566f32328f6/app/models/humongolus/__init__.py#L270) like it should be.

To demo this, first run `python app/models/test.py`, to see what the output _should_ look like. This file creates a simple user, assigns its values, and calls `.save()`, to store it in the DB. If you look at the console, you'll see that the [\_\_set\_\_() method](https://github.com/gopilot/backend/blob/bee4d092d01f282a8921e8aacf90a566f32328f6/app/models/humongolus/__init__.py#L270) is being correctly called, and that it's saving the correct User object to the DB.

Now, start the server using `python setup.py` and visit [/auth/test](http://localhost:5000/auth/test) in your browser. If you look at the console, you'll see that the \_\_set\_\_() method wasn't ever called, and the user object being saved in the DB isn't complete, missing all the values that were set.

[This route](https://github.com/gopilot/backend/blob/bee4d092d01f282a8921e8aacf90a566f32328f6/app/auth/__init__.py#L106) contains the exact same code as [test.py](https://github.com/gopilot/backend/blob/bee4d092d01f282a8921e8aacf90a566f32328f6/app/models/test.py), but for some reason \_\_set\_\_() isn't being called, and the data isn't being saved. 
