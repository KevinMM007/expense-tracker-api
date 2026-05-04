"""Aggregation/reporting endpoints."""

from __future__ import annotations

from datetime import date as date_type
from decimal import Decimal

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession
from app.crud import expense as expense_crud

router = APIRouter(prefix="/reports", tags=["reports"])


class TotalResponse(BaseModel):
    total: Decimal


class CategoryTotal(BaseModel):
    category_id: int
    category_name: str
    total: Decimal


class MonthTotal(BaseModel):
    year: int
    month: int
    total: Decimal


@router.get("/total", response_model=TotalResponse)
def total(
    db: DbSession,
    current_user: CurrentUser,
    date_from: date_type | None = Query(default=None),
    date_to: date_type | None = Query(default=None),
) -> TotalResponse:
    value = expense_crud.total_for_user(db, current_user.id, date_from, date_to)
    return TotalResponse(total=value)


@router.get("/by-category", response_model=list[CategoryTotal])
def by_category(
    db: DbSession,
    current_user: CurrentUser,
    date_from: date_type | None = Query(default=None),
    date_to: date_type | None = Query(default=None),
) -> list[CategoryTotal]:
    rows = expense_crud.totals_by_category(db, current_user.id, date_from, date_to)
    return [CategoryTotal(**r) for r in rows]


@router.get("/by-month", response_model=list[MonthTotal])
def by_month(
    db: DbSession,
    current_user: CurrentUser,
    year: int | None = Query(default=None, ge=2000, le=2100),
) -> list[MonthTotal]:
    rows = expense_crud.totals_by_month(db, current_user.id, year)
    return [MonthTotal(**r) for r in rows]
