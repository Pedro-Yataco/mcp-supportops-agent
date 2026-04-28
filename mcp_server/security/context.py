from dataclasses import dataclass

from app.config import get_settings
from db.connection import get_db_cursor


@dataclass(frozen=True)
class UserContext:
    user_id: int
    username: str
    full_name: str
    role_name: str


def get_current_user_context() -> UserContext:
    settings = get_settings()

    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                u.id AS user_id,
                u.username,
                u.full_name,
                r.name AS role_name
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE u.id = %s
              AND u.is_active = TRUE
            """,
            (settings.current_user_id,),
        )
        user = cursor.fetchone()

    if not user:
        raise PermissionError(
            f"Current user with id={settings.current_user_id} not found or inactive"
        )

    return UserContext(
        user_id=user["user_id"],
        username=user["username"],
        full_name=user["full_name"],
        role_name=user["role_name"],
    )