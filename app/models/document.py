import mongoengine as orm
from bson.dbref import DBRef
from bson.objectid import ObjectId
from datetime import datetime
from bson import json_util
import json

## Superclass of all our documents
class Document(orm.Document):
    meta = {
        'abstract': True
    }
    _hidden = []

    @classmethod
    def find_id(cls, id):
        try:
            oid = ObjectId(id)
        except:
            return False

        return cls.objects(id=oid).first()

    def to_dict(self, debug=False):
        data = {}
        if debug:
            print self._data

        for key, obj in self._data.iteritems():
            if not key in self._hidden and not key.startswith('_'):
                if type(obj) == list and len(obj) > 0:
                    if isinstance(obj[0], Document):
                        data[key] = [o.to_dict() for o in obj]
                    elif isinstance(obj[0], ObjectId) or isinstance(obj[0], datetime):
                        data[key] = [str(o) for o in obj]
                    elif isinstance(obj[0], DBRef):
                        data[key] = [str(o.id) for o in obj]
                    else:
                        data[key] = obj
                else:
                    if isinstance(obj, orm.Document):
                        data[key] = obj.to_dict()
                    elif isinstance(obj, ObjectId) or isinstance(obj, datetime):
                        data[key] = str(obj)
                    elif isinstance(obj, DBRef):
                        data[key] = str(obj.id)
                    else:
                        data[key] = obj
        return data

    def to_json(self, debug=False):
        return json.dumps(self.to_dict(debug=debug)), 200, {'Content-Type': 'application/json'}

def remove_hidden(obj, hidden):
    d = {}
    for k, o in obj.iteritems():
        if not k in hidden:
            if isinstance(o, Document):
                d[k] = remove_hidden(o._data, hidden)
            else:
                d[k] = o
    return d