from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  

# ------------------------
# Password helpers
# ------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _truncate_to_72_bytes(password: str) -> str:
    if not password:
        return ""
    b = password.encode("utf-8")
    return b[:72].decode("utf-8", errors="ignore")

def get_password_hash(password: str) -> str:
    truncated = _truncate_to_72_bytes(password)
    if not truncated:
        return ""
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, stored_password: str) -> bool:
    if not stored_password:
        return False
    try:
        truncated = _truncate_to_72_bytes(plain_password)
        return pwd_context.verify(truncated, stored_password)
    except Exception:
        return False

# ------------------------
# JWT helpers
# ------------------------
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt
