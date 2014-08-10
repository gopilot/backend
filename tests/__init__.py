import redis
import pymongo
import urlparse

import app as backend

backend.app.config['MONGO_DB'] = 'backend_test'
backend.app.config['REDIS_DB'] = 15
backend.start()

test_client = backend.app.test_client()

mongo_client = pymongo.MongoClient( backend.app.config['MONGO_URL'] )

redis_client = backend.sessions