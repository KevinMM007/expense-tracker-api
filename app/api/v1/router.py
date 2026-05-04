from fastapi import APIRouter

from app.api.v1 import auth, categories, expenses, reports

api_router = APIRouter()


@api_router.get("/ping", tags=["health"])
def ping() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(expenses.router)
api_router.include_router(reports.router)
