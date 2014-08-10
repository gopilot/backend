import mongoengine as orm
import json

## Superclass of all our documents
class Document(orm.Document):
    meta = {
        'abstract': True
    }
    _hidden = []

    def to_json_obj(self, populate=[]):
        ret = {}

        for key, obj in self._data.iteritems():
            if not key in self._hidden:
                try:
                    ret[key] = obj.to_json_obj()
                except:
                    try:
                        ret[key] = obj.json()
                    except:
                        try:
                            ret[key] = obj._json()
                        except:
                            ret[key] = str(obj)

        return ret;

    def to_json(self):
        return json.dumps(self.to_json_obj()), 200, {'Content-Type': 'application/json'}

    @classmethod
    def find_id(cls, oid):
        return cls.objects(id=oid).first()