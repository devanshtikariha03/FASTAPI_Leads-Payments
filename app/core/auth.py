# app/core/auth.py

import os
import time
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Load environment variables
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("Missing JWT_SECRET in .env")

# HTTPBearer instance for dependency
security = HTTPBearer()

def verify_jwt_token(creds: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify incoming JWT Bearer token.
    Raises 401 if invalid or expired.
    """
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    # Validate issuer and expiry
    if payload.get("iss") != "onecard" or payload.get("exp", 0) < time.time():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    return payload
