import logging
import warnings

from fastmcp import FastMCP

from app.config import get_settings
from mcp_server.tools.customers import register_customer_tools
from mcp_server.tools.security import register_security_tools
from mcp_server.tools.tickets import register_ticket_tools

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("fastmcp").setLevel(logging.WARNING)

settings = get_settings()

mcp = FastMCP("SupportOps MCP Server")

register_security_tools(mcp)
register_ticket_tools(mcp)
register_customer_tools(mcp)


if __name__ == "__main__":
    print(
        f"Starting SupportOps MCP Server on "
        f"http://{settings.mcp_server_host}:{settings.mcp_server_port}"
    )
    print(f"Internal API: {settings.internal_api_base_url}")
    print(f"Current simulated user id: {settings.current_user_id}")

    mcp.run(
        transport="http",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
    )