from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

import hashlib
import json

def generate_cryptographic_signature(payload: dict) -> str:
    # Remove mutable or system fields before hashing
    clean_payload = {k: v for k, v in payload.items() if k not in ["id", "created_at", "updated_at", "cryptographic_signature"]}
    # Sort keys for deterministic hashing
    encoded = json.dumps(clean_payload, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()
