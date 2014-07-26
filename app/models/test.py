import pymongo
import os

import humongolus as orm
from users import User


client = pymongo.MongoClient( os.getenv('MONGO_URL',    'mongodb://localhost:27017') )
orm.settings( client )

u = User()
u.type = "organizer"
u.name = "Test Organizer"
u.email = "test@gmail.com"
u.password = "test test"
u.save()