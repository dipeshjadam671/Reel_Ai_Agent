from backend.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    mask_secret
)

def test_password_hashing():
    pwd = "super-secret-password-123"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong-password", hashed) is False

def test_jwt_token_creation_and_decode():
    sub = "user-uuid-123"
    ws_id = "workspace-uuid-456"
    token = create_access_token(subject=sub, workspace_id=ws_id, role="owner")
    assert isinstance(token, str)
    payload = decode_access_token(token)
    assert payload.get("sub") == sub
    assert payload.get("workspace_id") == ws_id
    assert payload.get("role") == "owner"

def test_mask_secret():
    assert mask_secret("sk-1234567890abcdef") == "sk-1...cdef"
    assert mask_secret("short") == "********"
    assert mask_secret("") == ""
