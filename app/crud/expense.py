"""CRUD helpers for the Expense model. All queries are user-scoped."""

from __future__ import annotations

from datetime import date as date_type
from decimal import Decimal

from sqlalchemy import Numeric, cast, extract, func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def list_for_user(
    db: Session,
    user_id: int,
    category_id: int | None = None,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Expense]:
    stmt = select(Expense).where(Expense.user_id == user_id)
    if category_id is not None:
        stmt = stmt.where(Expense.category_id == category_id)
    if date_from is not None:
        stmt = stmt.where(Expense.spent_on >= date_from)
    if date_to is not None:
        stmt = stmt.where(Expense.spent_on <= date_to)
    stmt = stmt.order_by(Expense.spent_on.desc(), Expense.id.desc()).offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def get_for_user(db: Session, user_id: int, expense_id: int) -> Expense | None:
    stmt = select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def create(db: Session, user_id: int, payload: ExpenseCreate) -> Expense:
    expense = Expense(
        user_id=user_id,
        amount=payload.amount,
        description=payload.description,
        spent_on=payload.spent_on,
        category_id=payload.category_id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def update(db: Session, expense: Expense, payload: ExpenseUpdate) -> Expense:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(expense, key, value)
    db.commit()
    db.refresh(expense)
    return expense


def delete(db: Session, expense: Expense) -> None:
    db.delete(expense)
    db.commit()


# ---------- Reporting / aggregations ----------


def total_for_user(
    db: Session,
    user_id: int,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
) -> Decimal:
    stmt = select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.user_id == user_id)
    if date_from is not None:
        stmt = stmt.where(Expense.spent_on >= date_from)
    if date_to is not None:
        stmt = stmt.where(Expense.spent_on <= date_to)
    result = db.execute(stmt).scalar_one()
    return Decimal(result)


def totals_by_category(
    db: Session,
    user_id: int,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
) -> list[dict]:
    """Return [{category_id, category_name, total}, ...] sorted by total desc."""
    stmt = (
        select(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .where(Expense.user_id == user_id)
    )
    if date_from is not None:
        stmt = stmt.where(Expense.spent_on >= date_from)
    if date_to is not None:
        stmt = stmt.where(Expense.spent_on <= date_to)
    stmt = stmt.group_by(Category.id, Category.name).order_by(func.sum(Expense.amount).desc())
    rows = db.execute(stmt).all()
    return [
        {"category_id": r.category_id, "category_name": r.category_name, "total": Decimal(r.total)}
        for r in rows
    ]


def totals_by_month(
    db: Session,
    user_id: int,
    year: int | None = None,
) -> list[dict]:
    """Return [{year, month, total}, ...] sorted ascending."""
    year_col = cast(extract("year", Expense.spent_on), Numeric).label("y")
    month_col = cast(extract("month", Expense.spent_on), Numeric).label("m")
    stmt = (
        select(
            year_col,
            month_col,
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .where(Expense.user_id == user_id)
    )
    if year is not None:
        stmt = stmt.where(extract("year", Expense.spent_on) == year)
    stmt = stmt.group_by(year_col, month_col).order_by(year_col, month_col)
    rows = db.execute(stmt).all()
    return [
        {"year": int(r.y), "month": int(r.m), "total": Decimal(r.total)} for r in rows
    ]
