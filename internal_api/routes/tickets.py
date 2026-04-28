from fastapi import APIRouter, HTTPException, Query

from db.connection import get_db_cursor
from internal_api.schemas import (
    CreateInternalNoteRequest,
    CreateInternalNoteResponse,
    TicketCommentResponse,
    TicketPriority,
    TicketResponse,
    TicketStatus,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketResponse])
def list_tickets(
    status: TicketStatus | None = Query(default=None),
    priority: TicketPriority | None = Query(default=None),
    customer_id: int | None = Query(default=None, ge=1),
) -> list[dict]:
    filters = []
    params = []

    if status:
        filters.append("t.status = %s")
        params.append(status)

    if priority:
        filters.append("t.priority = %s")
        params.append(priority)

    if customer_id:
        filters.append("t.customer_id = %s")
        params.append(customer_id)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    query = f"""
        SELECT
            t.id,
            t.customer_id,
            c.name AS customer_name,
            t.title,
            t.description,
            t.priority,
            t.status,
            t.assigned_to,
            u.username AS assigned_to_username,
            t.created_at,
            t.updated_at
        FROM tickets t
        JOIN customers c ON c.id = t.customer_id
        LEFT JOIN users u ON u.id = t.assigned_to
        {where_clause}
        ORDER BY t.created_at DESC
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, tuple(params))
        return cursor.fetchall()


@router.get("/sla-risk/open")
def detect_open_ticket_sla_risk() -> list[dict]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                t.id AS ticket_id,
                t.title,
                t.priority,
                t.status,
                t.created_at,
                c.id AS customer_id,
                c.name AS customer_name,
                cs.resolution_time_hours,
                TIMESTAMPDIFF(HOUR, t.created_at, NOW()) AS age_hours,
                CASE
                    WHEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) >= cs.resolution_time_hours
                        THEN 'breached'
                    WHEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) >= cs.resolution_time_hours * 0.75
                        THEN 'at_risk'
                    ELSE 'healthy'
                END AS sla_status
            FROM tickets t
            JOIN customers c ON c.id = t.customer_id
            JOIN customer_slas cs
                ON cs.customer_id = t.customer_id
               AND cs.priority = t.priority
            WHERE t.status IN ('open', 'in_progress')
            ORDER BY
                CASE
                    WHEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) >= cs.resolution_time_hours
                        THEN 1
                    WHEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) >= cs.resolution_time_hours * 0.75
                        THEN 2
                    ELSE 3
                END,
                t.priority ASC,
                t.created_at ASC
            """
        )

        return cursor.fetchall()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int) -> dict:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                t.id,
                t.customer_id,
                c.name AS customer_name,
                t.title,
                t.description,
                t.priority,
                t.status,
                t.assigned_to,
                u.username AS assigned_to_username,
                t.created_at,
                t.updated_at
            FROM tickets t
            JOIN customers c ON c.id = t.customer_id
            LEFT JOIN users u ON u.id = t.assigned_to
            WHERE t.id = %s
            """,
            (ticket_id,),
        )
        ticket = cursor.fetchone()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@router.get("/{ticket_id}/comments", response_model=list[TicketCommentResponse])
def list_ticket_comments(ticket_id: int) -> list[dict]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id
            FROM tickets
            WHERE id = %s
            """,
            (ticket_id,),
        )
        ticket = cursor.fetchone()

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        cursor.execute(
            """
            SELECT
                tc.id,
                tc.ticket_id,
                tc.author_user_id,
                u.username AS author_username,
                tc.comment,
                tc.is_internal,
                tc.created_at
            FROM ticket_comments tc
            JOIN users u ON u.id = tc.author_user_id
            WHERE tc.ticket_id = %s
            ORDER BY tc.created_at ASC
            """,
            (ticket_id,),
        )
        return cursor.fetchall()


@router.post("/{ticket_id}/internal-note", response_model=CreateInternalNoteResponse)
def add_internal_note(
    ticket_id: int,
    payload: CreateInternalNoteRequest,
) -> dict:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id
            FROM tickets
            WHERE id = %s
            """,
            (ticket_id,),
        )
        ticket = cursor.fetchone()

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE id = %s AND is_active = TRUE
            """,
            (payload.author_user_id,),
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="Author user not found")

        cursor.execute(
            """
            INSERT INTO ticket_comments (
                ticket_id,
                author_user_id,
                comment,
                is_internal
            )
            VALUES (%s, %s, %s, TRUE)
            """,
            (ticket_id, payload.author_user_id, payload.comment),
        )

        comment_id = cursor.lastrowid

    return {
        "message": "Internal note created",
        "comment_id": comment_id,
    }
