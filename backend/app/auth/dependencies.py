from fastapi import Header, HTTPException
from app.auth.security import decode_access_token
from app.repositories.users import get_user_by_id


def get_current_user(authorization: str = Header(None)):
    """
    Expects header: Authorization: Bearer <token>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    token = authorization.split(" ", 1)[1]
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")

    return user  # {"id": ..., "email": ...}
