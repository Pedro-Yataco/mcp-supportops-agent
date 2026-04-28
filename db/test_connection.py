from db.connection import get_db_cursor


def main() -> None:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                u.id,
                u.username,
                u.full_name,
                r.name AS role_name
            FROM users u
            JOIN roles r ON r.id = u.role_id
            ORDER BY u.id
            """
        )
        users = cursor.fetchall()

    print("Database connection OK")
    print("Users:")
    for user in users:
        print(
            f"- {user['id']}: {user['username']} "
            f"({user['full_name']}) -> {user['role_name']}"
        )


if __name__ == "__main__":
    main()