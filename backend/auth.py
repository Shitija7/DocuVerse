from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------------
# Password helpers
# ------------------------

def _prehash_password(password: str) -> str:
    """
    Allows any length password by pre-hashing it with SHA256 before bcrypt.
    This ensures consistent security while staying bcrypt-compatible.
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    sha = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return sha  # always 64 hex chars, well under 72 bytes


def get_password_hash(password: str) -> str:
    prehashed = _prehash_password(password)
    return pwd_context.hash(prehashed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    prehashed = _prehash_password(plain_password)
    return pwd_context.verify(prehashed, hashed_password)

# ------------------------
# JWT helpers
# ------------------------

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt
