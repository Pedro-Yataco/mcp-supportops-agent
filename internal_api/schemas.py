from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


TicketPriority = Literal["P1", "P2", "P3"]
TicketStatus = Literal[
    "open",
    "in_progress",
    "waiting_customer",
    "resolved",
    "closed",
]
CustomerTier = Literal["standard", "premium", "enterprise"]


class CustomerResponse(BaseModel):
    id: int
    name: str
    tier: CustomerTier
    industry: str | None = None
    is_active: bool


class CustomerSLAResponse(BaseModel):
    id: int
    customer_id: int
    priority: TicketPriority
    response_time_hours: int
    resolution_time_hours: int


class TicketResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: str
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    assigned_to: int | None = None
    assigned_to_username: str | None = None
    created_at: datetime
    updated_at: datetime


class TicketCommentResponse(BaseModel):
    id: int
    ticket_id: int
    author_user_id: int
    author_username: str
    comment: str
    is_internal: bool
    created_at: datetime


class CreateInternalNoteRequest(BaseModel):
    author_user_id: int = Field(..., ge=1)
    comment: str = Field(..., min_length=3, max_length=2000)


class CreateInternalNoteResponse(BaseModel):
    message: str
    comment_id: int