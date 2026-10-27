import uuid

from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import Error as MySQLError

from backend.config.logging_setting import setup_logger
from backend.src.auth.admin_auth import verify_admin
from backend.src.schema.schema import NewUser
from backend.src.utils.db_connection import OpenDb
from backend.src.utils.hash_password import hash_password

router = APIRouter()
logger = setup_logger("register_endpoint")


@router.post("/register")
def register(data: NewUser, claims=Depends(verify_admin)):
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(data.password)
    username = data.username
    role = data.role.value

    try:
        with OpenDb() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="User already exists")

            cursor.execute("SELECT id FROM roles WHERE role = %s", (role,))
            role_record = cursor.fetchone()
            if not role_record:
                raise HTTPException(status_code=400, detail="Role does not exist")

            cursor.execute(
                """
                INSERT INTO users (id, username, password, role_id)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, username, hashed_password, role_record[0]),
            )

        logger.info("Admin %s created account for user '%s'", claims.get("sub"), username)
        return {"message": f"Account created for {username}"}

    except HTTPException:
        raise
    except MySQLError:
        logger.exception("Database error while creating user '%s'", username)
        raise HTTPException(status_code=500, detail="Database error")
    except Exception:
        logger.exception("Unexpected error while creating user '%s'", username)
        raise HTTPException(status_code=500, detail="Unexpected error while creating user")
