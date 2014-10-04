from pymongo import mongo_client
## Value copied from heroku's website:
mongo_client = mongo_client.MongoClient( 'mongodb://heroku:au50UY2y2vx-pVXyvDey5w6Cj8cSCvTDTcGUK4PMQtCC4-aJkpLvmRElasCb8KW3Uwg7i_vn3r9U0Ibjz5h2YA@kahana.mongohq.com:10079/app26071927' )
print(mongo_client)