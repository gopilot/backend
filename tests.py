from flask import Flask

import app as backend

import unittest
import json
import pymongo
import redis
import time
import datetime


backend.app.config['MONGO_DB'] = 'backend_test'
backend.app.config['REDIS_DB'] = 15
backend.start()

global test_client
test_client = backend.app.test_client()

import tests.auth
import tests.events
import tests.users


if __name__ == '__main__':
    unittest.main()
