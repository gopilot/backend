import humongolus as orm

## Superclass of all our documents
class Document(orm.Document):
    _hidden = []
    _db = 'backend'

    def to_json(self):
        ret = []
        for key, obj in self:
            if not key in self._hidden:
                try:
                    ret.append(obj.to_json())
                except:
                    try:
                        ret.append(obj._json())
                    except:
                        ret.append(obj)
        return ret