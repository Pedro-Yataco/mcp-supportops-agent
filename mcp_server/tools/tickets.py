from mcp_server import internal_api_client
from mcp_server.formatters import (
    format_sla_risk_report,
    format_ticket_list,
    to_pretty_json,
)
from mcp_server.security.context import get_current_user_context
from mcp_server.security.permissions import require_permission


def register_ticket_tools(mcp):
    @mcp.tool()
    def list_open_tickets(priority: str | None = None, customer_id: int | None = None) -> str:
        """List open support tickets, optionally filtered by priority or customer_id.

        Args:
            priority: Optional ticket priority. Allowed values: P1, P2, P3.
            customer_id: Optional customer ID.
        """
        user = get_current_user_context()
        require_permission(user, "tickets.read")

        tickets = internal_api_client.list_tickets(
            status="open",
            priority=priority,
            customer_id=customer_id,
        )
        return format_ticket_list(tickets)

    @mcp.tool()
    def get_ticket_detail(ticket_id: int, include_comments: bool = True) -> str:
        """Get detailed information about a support ticket.

        Args:
            ticket_id: Ticket ID to retrieve.
            include_comments: Whether to include internal ticket comments.
        """
        user = get_current_user_context()
        require_permission(user, "tickets.read")

        ticket = internal_api_client.get_ticket(ticket_id)

        if include_comments:
            comments = internal_api_client.list_ticket_comments(ticket_id)
            return to_pretty_json(
                {
                    "ticket": ticket,
                    "comments": comments,
                }
            )

        return to_pretty_json(ticket)

    @mcp.tool()
    def add_internal_note(ticket_id: int, comment: str) -> str:
        """Add an internal note to a support ticket.

        Args:
            ticket_id: Ticket ID where the note should be added.
            comment: Internal note content.
        """
        user = get_current_user_context()
        require_permission(user, "tickets.comment.internal")

        result = internal_api_client.add_internal_note(
            ticket_id=ticket_id,
            author_user_id=user.user_id,
            comment=comment,
        )

        return to_pretty_json(
            {
                "message": "Internal note added successfully",
                "result": result,
                "performed_by": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "role": user.role_name,
                },
            }
        )
    
    @mcp.tool()
    def detect_sla_risk() -> str:
        """Detect open or in-progress tickets that are at risk of breaching SLA.

        Requires manager-level permission.
        """
        user = get_current_user_context()
        require_permission(user, "sla.risk.detect")

        risk_items = internal_api_client.detect_open_ticket_sla_risk()
        return format_sla_risk_report(risk_items)