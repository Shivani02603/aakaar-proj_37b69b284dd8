import os
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from database.models import User
from database.config import get_db

# Constants
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    raise ValueError('JWT_SECRET env var is not set')

ALGORITHM = "HS256"

# Password hashing functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# JWT token functions
def create_access_token(data: dict) -> str:
    data['exp'] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(data, JWT_SECRET, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# FastAPI dependency to get current user
security = HTTPBearer()

async def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")