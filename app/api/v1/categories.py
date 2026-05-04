"""Category endpoints (user-scoped)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import CurrentUser, DbSession
from app.crud import category as category_crud
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(db: DbSession, current_user: CurrentUser) -> list[CategoryRead]:
    return category_crud.list_for_user(db, current_user.id)  # type: ignore[return-value]


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate, db: DbSession, current_user: CurrentUser
) -> CategoryRead:
    if category_crud.get_by_name(db, current_user.id, payload.name) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists",
        )
    return category_crud.create(db, current_user.id, payload)  # type: ignore[return-value]


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    category_id: int, db: DbSession, current_user: CurrentUser
) -> CategoryRead:
    category = category_crud.get_for_user(db, current_user.id, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category  # type: ignore[return-value]


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> CategoryRead:
    category = category_crud.get_for_user(db, current_user.id, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if payload.name is not None and payload.name != category.name:
        existing = category_crud.get_by_name(db, current_user.id, payload.name)
        if existing is not None and existing.id != category.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists",
            )
    return category_crud.update(db, category, payload)  # type: ignore[return-value]


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_category(category_id: int, db: DbSession, current_user: CurrentUser) -> Response:
    category = category_crud.get_for_user(db, current_user.id, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category_crud.delete(db, category)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
