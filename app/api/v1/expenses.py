"""Expense endpoints (user-scoped) with optional filters."""

from __future__ import annotations

from datetime import date as date_type

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.api.deps import CurrentUser, DbSession
from app.crud import category as category_crud
from app.crud import expense as expense_crud
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["expenses"])


def _ensure_category_belongs_to_user(db, user_id: int, category_id: int) -> None:
    if category_crud.get_for_user(db, user_id, category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id does not belong to current user",
        )


@router.get("", response_model=list[ExpenseRead])
def list_expenses(
    db: DbSession,
    current_user: CurrentUser,
    category_id: int | None = Query(default=None),
    date_from: date_type | None = Query(default=None),
    date_to: date_type | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[ExpenseRead]:
    return expense_crud.list_for_user(  # type: ignore[return-value]
        db,
        current_user.id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate, db: DbSession, current_user: CurrentUser
) -> ExpenseRead:
    _ensure_category_belongs_to_user(db, current_user.id, payload.category_id)
    return expense_crud.create(db, current_user.id, payload)  # type: ignore[return-value]


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(
    expense_id: int, db: DbSession, current_user: CurrentUser
) -> ExpenseRead:
    expense = expense_crud.get_for_user(db, current_user.id, expense_id)
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense  # type: ignore[return-value]


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ExpenseRead:
    expense = expense_crud.get_for_user(db, current_user.id, expense_id)
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    if payload.category_id is not None and payload.category_id != expense.category_id:
        _ensure_category_belongs_to_user(db, current_user.id, payload.category_id)
    return expense_crud.update(db, expense, payload)  # type: ignore[return-value]


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_expense(expense_id: int, db: DbSession, current_user: CurrentUser) -> Response:
    expense = expense_crud.get_for_user(db, current_user.id, expense_id)
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    expense_crud.delete(db, expense)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
