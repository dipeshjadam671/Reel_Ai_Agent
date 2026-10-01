import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, AttributeError):
        return False
