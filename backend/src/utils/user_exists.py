from backend.src.utils.db_connection import OpenDb


def user_exists(user_id: str) -> bool:
    with OpenDb() as cursor:
        cursor.execute("SELECT 1 FROM users WHERE id=%s", (user_id,))
        return cursor.fetchone() is not None
