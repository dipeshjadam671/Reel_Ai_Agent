import json
from datetime import date, datetime
from uuid import UUID

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

def dumps(obj, **kwargs) -> str:
    return json.dumps(obj, cls=CustomJSONEncoder, **kwargs)

def loads(s, **kwargs):
    return json.loads(s, **kwargs)
