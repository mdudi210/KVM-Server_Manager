from fastapi import APIRouter, Depends, Response
from fastapi_jwt_auth import AuthJWT

from backend.src.schema.schema import LoginRequest
from backend.src.services.login import login as unified_login

router = APIRouter()


@router.post("/adlogin", deprecated=True)
def ad_login(data: LoginRequest, response: Response, Authorize: AuthJWT = Depends()):
    payload = data.copy(update={"auth_provider": "ad"})
    return unified_login(payload, response, Authorize)
