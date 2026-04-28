from mcp_server.formatters import to_pretty_json
from mcp_server.security.context import get_current_user_context


def register_security_tools(mcp):
    @mcp.tool()
    def whoami() -> str:
        """Return the current simulated user context."""
        user = get_current_user_context()
        return to_pretty_json(
            {
                "user_id": user.user_id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role_name,
            }
        )