import humongolus as orm
from app import app
from bson.objectid import ObjectId
import json

## Superclass of all our documents
class Document(orm.Document):
    _hidden = []
    _db = app.config['MONGO_DB']
    created = ""
    modified = ""

    def to_json(self):
        ret = {}
        self.created = str(self.__created__)
        self.modified = str(self.__modified__)

        for key, obj in self.__dict__.iteritems():
            if ( not key in self._hidden ) and ( not key.startswith("_") ) and ( not key == '_id' ):
                try:
                    ret[key] = obj.to_json()
                except:
                    try:
                        ret[key] = obj._json()
                    except:
                        ret[key] = str(obj)
        return json.dumps(ret)

    @classmethod
    def find_id(cls, id):

        return super(Document, cls).find_one({ '_id': ObjectId(id) });