import humongolus as orm
from app import app
from bson.objectid import ObjectId
from bson import json_util
import json
import datetime

## Superclass of all our documents
class Document(orm.Document):
    _hidden = []
    _db = app.config['MONGO_DB']
    created = ""
    modified = ""

    def to_json_obj(self, populate=[]):
        ret = {}
        self.created = str(self.__created__)
        self.modified = str(self.__modified__)

        for key, obj in self.__dict__.iteritems():
            if (( not key in self._hidden ) and ( not key.startswith("_") )) or ( key == '_id' ):     
                try:
                    ret[key] = obj.to_json()
                except:
                    try:
                        ret[key] = obj._json()
                    except:
                        ret[key] = str(obj)

        for field in populate:
            if ret[field]:
                print 'field', ret[field]
                ret[field] = self.__class__.find_id( str(ret[field]) )

        return ret;

    def to_json(self, populate=[]):
        return json.dumps( self.to_json_obj(populate=populate), default=json_util.default ), 200, {'Content-Type': 'application/json'}

    @classmethod
    def find_id(cls, id):
        print "finding", id
        return super(Document, cls).find_one({ '_id': ObjectId(id) });