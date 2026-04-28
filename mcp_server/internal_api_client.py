from typing import Any

import httpx

from app.config import get_settings


class InternalAPIError(RuntimeError):
    pass


def _base_url() -> str:
    return get_settings().internal_api_base_url.rstrip("/")


def _handle_response(response: httpx.Response) -> Any:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise InternalAPIError(
            f"Internal API error {response.status_code}: {response.text}"
        ) from exc

    return response.json()


def list_tickets(
    status: str | None = None,
    priority: str | None = None,
    customer_id: int | None = None,
) -> Any:
    params: dict[str, Any] = {}

    if status:
        params["status"] = status

    if priority:
        params["priority"] = priority

    if customer_id:
        params["customer_id"] = customer_id

    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{_base_url()}/tickets", params=params)
        return _handle_response(response)


def get_ticket(ticket_id: int) -> Any:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{_base_url()}/tickets/{ticket_id}")
        return _handle_response(response)


def list_ticket_comments(ticket_id: int) -> Any:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{_base_url()}/tickets/{ticket_id}/comments")
        return _handle_response(response)


def add_internal_note(ticket_id: int, author_user_id: int, comment: str) -> Any:
    payload = {
        "author_user_id": author_user_id,
        "comment": comment,
    }

    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            f"{_base_url()}/tickets/{ticket_id}/internal-note",
            json=payload,
        )
        return _handle_response(response)


def list_customers() -> Any:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{_base_url()}/customers")
        return _handle_response(response)


def get_customer(customer_id: int) -> Any:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{_base_url()}/customers/{customer_id}")
        return _handle_response(response)


def get_customer_sla(customer_id: int) -> Any:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{_base_url()}/customers/{customer_id}/sla")
        return _handle_response(response)