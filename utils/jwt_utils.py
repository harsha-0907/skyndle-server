
import jwt
import time
from datetime import datetime, timedelta
from enum import Enum
from datamodels.variables import fetch_key_from_env

class JWTStatus(Enum):
    OK = "OK"
    EXPIRED = "EXPIRED"
    INVALID = "INVALID"

JWT_SECRET_KEY = fetch_key_from_env("jwt_secret_key") or "a-string-secret-at-least-256-bits-long"

def encode_jwt(data_to_encode: dict, expires_in: int = 3600):
    """ Encode a dictionary into a JWT token"""

    time_now = datetime.utcnow()
    valid_upto = time_now + timedelta(seconds=expires_in)
    payload = data_to_encode.copy()
    payload["exp"] = valid_upto

    jwt_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return jwt_token

def decode_jwt(jwt_token: str):
    """ Decodes a JWT Token & returns status with data decoded"""

    try:
        decoded_data = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=["HS256"])
        return JWTStatus.OK, decoded_data

    except jwt.ExpiredSignatureError:
        decoded_data = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
        return JWTStatus.EXPIRED, decoded_data

    except (jwt.InvalidIssuerError, jwt.InvalidTokenError):
        return JWTStatus.INVALID, None

    except Exception:
        return JWTStatus.INVALID, None

