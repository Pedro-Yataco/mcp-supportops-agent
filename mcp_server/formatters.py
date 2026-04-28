import json
from typing import Any


def to_pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def format_ticket_list(tickets: list[dict]) -> str:
    if not tickets:
        return "No tickets found."

    lines = []
    for ticket in tickets:
        lines.append(
            f"[#{ticket['id']}] {ticket['priority']} | {ticket['status']} | "
            f"{ticket['customer_name']} | {ticket['title']}"
        )

    return "\n".join(lines)


def format_customer_list(customers: list[dict]) -> str:
    if not customers:
        return "No customers found."

    lines = []
    for customer in customers:
        lines.append(
            f"[{customer['id']}] {customer['name']} "
            f"({customer['tier']}, {customer.get('industry')})"
        )

    return "\n".join(lines)