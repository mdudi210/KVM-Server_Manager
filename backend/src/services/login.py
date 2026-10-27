import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi_jwt_auth import AuthJWT
from mysql.connector import Error as MySQLError

from backend.config import JWT_auth_setting
from backend.config.logging_setting import setup_logger
from backend.src.schema.schema import LoginRequest
from backend.src.utils.auth_ad import authenticate_with_ad
from backend.src.utils.db_connection import OpenDb
from backend.src.utils.hash_password import verify_password

load_dotenv()

router = APIRouter()
logger = setup_logger("login_endpoint")
RETURN_TOKEN_IN_BODY = os.getenv("RETURN_TOKEN_IN_BODY", "true").lower() in {"1", "true", "yes"}


def _authenticate_local(username: str, password: str) -> tuple[str, str, str]:
    with OpenDb() as cursor:
        cursor.execute(
            """
            SELECT u.id, u.username, u.password, r.role
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE u.username = %s
            """,
            (username,),
        )
        result = cursor.fetchone()

    if not result or not verify_password(password, result[2]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return result[0], result[1], result[3]


def _authenticate_ad(username: str, password: str) -> tuple[str, str, str]:
    result = authenticate_with_ad(username, password)
    if not result[0]:
        raise HTTPException(status_code=401, detail="Invalid AD credentials")
    return result[2], username, result[1]


def _build_login_response(
    *,
    response: Response,
    authorize: AuthJWT,
    user_id: str,
    username: str,
    role: str,
    auth_provider: str,
) -> dict:
    access_token = authorize.create_access_token(
        subject=username,
        expires_time=timedelta(days=7),
        user_claims={"id": user_id, "role": role},
    )

    authorize.set_access_cookies(access_token, response)

    payload = {
        "id": user_id,
        "username": username,
        "role": role,
        "auth_provider": auth_provider,
    }

    if RETURN_TOKEN_IN_BODY:
        payload["access_token"] = access_token

    return payload


@router.post("/login")
def login(data: LoginRequest, response: Response, Authorize: AuthJWT = Depends()):
    try:
        if data.auth_provider == "ad":
            user_id, username, role = _authenticate_ad(data.username, data.password)
        else:
            user_id, username, role = _authenticate_local(data.username, data.password)

        logger.info("User '%s' logged in successfully via %s", username, data.auth_provider)
        return _build_login_response(
            response=response,
            authorize=Authorize,
            user_id=user_id,
            username=username,
            role=role,
            auth_provider=data.auth_provider,
        )

    except HTTPException:
        raise
    except MySQLError:
        logger.exception("Database error occurred during login")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        logger.exception("Unexpected error in login API")
        raise HTTPException(status_code=500, detail="Unexpected error in login API")


@router.post("/logout")
def logout(response: Response, Authorize: AuthJWT = Depends()):
    Authorize.unset_jwt_cookies(response)
    return {"message": "Logged out successfully"}
