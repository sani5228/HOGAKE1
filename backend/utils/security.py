import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from backend.config import Config

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    return check_password_hash(hashed_password, plain_password)

def create_jwt_token(payload: dict) -> str:
    """Creates a JWT token with configured expiration."""
    exp = datetime.now(timezone.utc) + timedelta(hours=Config.JWT_EXPIRY_HOURS)
    token_payload = {
        **payload,
        "exp": exp,
        "iat": datetime.now(timezone.utc)
    }
    token = jwt.encode(token_payload, Config.JWT_SECRET, algorithm="HS256")
    return token

def decode_jwt_token(token: str) -> dict:
    """Decodes and validates a JWT token."""
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid authentication token")

def hash_aadhaar(aadhaar: str) -> str:
    """Hashes Aadhaar with salt for database storage and duplicate check."""
    salt = Config.JWT_SECRET[:16]
    return hashlib.sha256(f"{salt}:{aadhaar}".encode('utf-8')).hexdigest()

def mask_aadhaar(aadhaar: str) -> str:
    """Returns only the last 4 digits (XXXX-XXXX-1234)."""
    clean = str(aadhaar).replace('-', '').replace(' ', '')
    if len(clean) >= 4:
        return clean[-4:]
    return "XXXX"
