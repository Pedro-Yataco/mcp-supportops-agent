from fastapi import FastAPI

from internal_api.routes.customers import router as customers_router
from internal_api.routes.tickets import router as tickets_router

app = FastAPI(
    title="SupportOps Internal API",
    description="Simulated internal support operations API for MCP tools.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "supportops-internal-api",
    }


app.include_router(customers_router)
app.include_router(tickets_router)