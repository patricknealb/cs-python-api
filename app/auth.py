from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.backends import default_backend
import httpx
import json
from app.config import settings

security = HTTPBearer()

_public_key = None

async def get_public_key():
    global _public_key
    if _public_key is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.supabase_url}/auth/v1/.well-known/jwks.json",
                headers={"apikey": settings.supabase_anon_key}
            )
            data = response.json()
            _public_key = data["keys"][0]
    return _public_key

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        public_key = await get_public_key()

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            options={"verify_aud": False}
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return payload
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )