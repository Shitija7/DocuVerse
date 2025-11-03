from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv
from passlib.context import CryptContext  # 🔒 for hashing

load_dotenv()

# ------------------------
# JWT Config
# ------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# ------------------------
# Password helpers
# ------------------------
pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto"
)

def get_password_hash(password: str) -> str:
    """Hash the plain password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if plain password matches the stored hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------
# JWT helpers
# ------------------------
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a signed JWT token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt
