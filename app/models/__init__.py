"""SQLAlchemy ORM models.

Importing this package ensures every model is registered on ``Base.metadata``
so Alembic autogenerate and ``Base.metadata.create_all`` see all tables.
"""

from app.models.base import Base, TimestampMixin
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User

__all__ = ["Base", "Category", "Expense", "TimestampMixin", "User"]
