"""Expose all models so Alembic can discover them via Base.metadata."""
from app.db.database import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.account import Account  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401
from app.models.category_rule import CategoryRule  # noqa: F401
from app.models.budget import Budget  # noqa: F401
from app.models.alert import Alert  # noqa: F401
from app.models.bill import Bill  # noqa: F401
from app.models.reward import Reward  # noqa: F401

__all__ = ["Base", "User", "Account", "Transaction", "CategoryRule", "Budget", "Alert", "Bill", "Reward"]
