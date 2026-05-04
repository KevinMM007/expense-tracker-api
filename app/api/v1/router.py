from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/ping", tags=["health"])
def ping() -> dict[str, str]:
    return {"status": "ok"}
