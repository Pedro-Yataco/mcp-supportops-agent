from db.connection import get_db_cursor
from mcp_server.security.context import UserContext


def user_has_permission(user_id: int, permission_code: str) -> bool:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM users u
            JOIN role_permissions rp ON rp.role_id = u.role_id
            JOIN permissions p ON p.id = rp.permission_id
            WHERE u.id = %s
              AND u.is_active = TRUE
              AND p.code = %s
            LIMIT 1
            """,
            (user_id, permission_code),
        )
        return cursor.fetchone() is not None


def require_permission(user: UserContext, permission_code: str) -> None:
    if not user_has_permission(user.user_id, permission_code):
        raise PermissionError(
            f"Access denied: user '{user.username}' with role '{user.role_name}' "
            f"does not have permission '{permission_code}'"
        )