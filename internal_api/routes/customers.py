from fastapi import APIRouter, HTTPException

from db.connection import get_db_cursor
from internal_api.schemas import CustomerResponse, CustomerSLAResponse

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerResponse])
def list_customers() -> list[dict]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, tier, industry, is_active
            FROM customers
            ORDER BY id
            """
        )
        return cursor.fetchall()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int) -> dict:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, tier, industry, is_active
            FROM customers
            WHERE id = %s
            """,
            (customer_id,),
        )
        customer = cursor.fetchone()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.get("/{customer_id}/sla", response_model=list[CustomerSLAResponse])
def get_customer_sla(customer_id: int) -> list[dict]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id
            FROM customers
            WHERE id = %s
            """,
            (customer_id,),
        )
        customer = cursor.fetchone()

        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        cursor.execute(
            """
            SELECT id, customer_id, priority, response_time_hours, resolution_time_hours
            FROM customer_slas
            WHERE customer_id = %s
            ORDER BY priority
            """,
            (customer_id,),
        )
        return cursor.fetchall()