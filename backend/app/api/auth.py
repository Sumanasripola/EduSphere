from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.auth.security import hash_password, verify_password, create_access_token
from app.repositories.users import create_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(req: RegisterRequest):
    if get_user_by_email(req.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(req.password)
    user = create_user(req.email, hashed)
    token = create_access_token(user["id"])
    return {"access_token": token, "user": user}


@router.post("/login")
def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user["id"])
    return {"access_token": token, "user": {"id": user["id"], "email": user["email"]}}
