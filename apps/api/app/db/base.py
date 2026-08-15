from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


# Import models here so Alembic's autogenerate can discover them via
# Base.metadata without every model module needing to be imported manually.
from app.models import user  # noqa: E402,F401
