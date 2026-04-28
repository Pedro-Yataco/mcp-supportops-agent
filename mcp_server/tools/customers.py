from mcp_server import internal_api_client
from mcp_server.formatters import format_customer_list, to_pretty_json
from mcp_server.security.context import get_current_user_context
from mcp_server.security.permissions import require_permission


def register_customer_tools(mcp):
    @mcp.tool()
    def list_customers() -> str:
        """List active customers."""
        user = get_current_user_context()
        require_permission(user, "customers.read")

        customers = internal_api_client.list_customers()
        return format_customer_list(customers)

    @mcp.tool()
    def get_customer_profile(customer_id: int) -> str:
        """Get customer profile information.

        Args:
            customer_id: Customer ID to retrieve.
        """
        user = get_current_user_context()
        require_permission(user, "customers.read")

        customer = internal_api_client.get_customer(customer_id)
        return to_pretty_json(customer)

    @mcp.tool()
    def get_customer_sla(customer_id: int) -> str:
        """Get SLA rules for a customer.

        Args:
            customer_id: Customer ID.
        """
        user = get_current_user_context()
        require_permission(user, "sla.read")

        sla = internal_api_client.get_customer_sla(customer_id)
        return to_pretty_json(sla)