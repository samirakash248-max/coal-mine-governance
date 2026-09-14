import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.user import Role

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[Role] = None

class Login(BaseModel):
    email: str
    password: str

class GoogleAuthCallback(BaseModel):
    code: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str
