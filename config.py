import os

class Config(object):
	DEBUG = False
	TESTING = False
	MONGO_URL = "mongodb://localhost:27017"
	MONGO_DB = "backend"
	REDIS_URL = "redis://localhost:6379"
	REDIS_DB = 0

class DevelopmentConfig(Config):
	DEBUG = True

class TestingConfig(Config):
	DEBUG = True
	TESTING = True
	MONGO_DB = "backend_test"
	REDIS_DB = 15

class ProductionConfig(Config):
	DEBUG = False
	MONGO_URL = os.getenv("MONGOHQ_URL", "mongodb://localhost:27017")
	REDIS_URL = os.getenv("REDISCLOUD_URL", "redis://localhost:6379")