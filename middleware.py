# backend/middleware.py
import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer = HTTPBearer()
load_dotenv()
secret_key = os.getenv("secret_key", "supersecretkey")

def verify_token(request: HTTPAuthorizationCredentials = Security(bearer)):
    token = request.credentials
    try:
        # Decode token
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return {
            "id": payload.get("id"),
            "email": payload.get("email"),
            "userType": payload.get("userType"), # Safely get userType
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")