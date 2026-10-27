from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

from backend.src.schema.schema import Roles


def verify_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        claims = Authorize.get_raw_jwt()
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or missing token: {str(e)}")

    role = claims.get("role")
    user_id = claims.get("id")

    if not role or role not in {r.value for r in Roles}:
        raise HTTPException(status_code=403, detail="User access required")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user id in token claims")

    return claims
