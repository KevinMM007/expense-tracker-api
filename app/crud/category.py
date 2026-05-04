"""CRUD helpers for the Category model.

All queries are user-scoped: a user can only see/modify their own categories.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_for_user(db: Session, user_id: int) -> list[Category]:
    stmt = select(Category).where(Category.user_id == user_id).order_by(Category.name)
    return list(db.execute(stmt).scalars().all())


def get_for_user(db: Session, user_id: int, category_id: int) -> Category | None:
    stmt = select(Category).where(Category.id == category_id, Category.user_id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def get_by_name(db: Session, user_id: int, name: str) -> Category | None:
    stmt = select(Category).where(Category.user_id == user_id, Category.name == name)
    return db.execute(stmt).scalar_one_or_none()


def create(db: Session, user_id: int, payload: CategoryCreate) -> Category:
    category = Category(name=payload.name, user_id=user_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update(db: Session, category: Category, payload: CategoryUpdate) -> Category:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()
