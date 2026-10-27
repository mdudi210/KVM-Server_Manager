from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT


def verify_admin(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        claims = Authorize.get_raw_jwt()
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or missing token: {str(e)}")

    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if not claims.get("id"):
        raise HTTPException(status_code=400, detail="Missing user id in token claims")

    return claims
