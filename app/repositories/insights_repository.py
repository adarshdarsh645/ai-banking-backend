import uuid
from decimal import Decimal
from typing import Sequence

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.transaction import Transaction


class InsightsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_stmt(self, user_id: uuid.UUID):
        return (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
        )

    async def get_cashflow_by_month(
        self, user_id: uuid.UUID
    ) -> Sequence[tuple]:
        """Returns (year, month, txn_type, total) grouped by month."""
        from sqlalchemy import extract
        stmt = (
            select(
                extract("year", Transaction.txn_date).label("year"),
                extract("month", Transaction.txn_date).label("month"),
                Transaction.txn_type,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .group_by("year", "month", Transaction.txn_type)
            .order_by("year", "month")
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_top_merchants(
        self, user_id: uuid.UUID, limit: int = 10
    ) -> Sequence[tuple]:
        """Returns (merchant, total) ordered by total DESC."""
        stmt = (
            select(
                Transaction.merchant,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Account, Transaction.account_id == Account.id)
            .where(
                Account.user_id == user_id,
                Transaction.txn_type == "debit",
                Transaction.merchant.isnot(None),
            )
            .group_by(Transaction.merchant)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_category_spend(
        self, user_id: uuid.UUID
    ) -> Sequence[tuple]:
        """Returns (category, total) for debit transactions."""
        stmt = (
            select(
                Transaction.category,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id, Transaction.txn_type == "debit")
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_category_spend_by_month(
        self, user_id: uuid.UUID, month: int, year: int
    ) -> Sequence[tuple]:
        """Returns (category, total) for debit transactions in a specific month/year."""
        stmt = (
            select(
                Transaction.category,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Account, Transaction.account_id == Account.id)
            .where(
                Account.user_id == user_id,
                Transaction.txn_type == "debit",
                extract("month", Transaction.txn_date) == month,
                extract("year", Transaction.txn_date) == year,
            )
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_all_transactions(
        self, user_id: uuid.UUID
    ) -> Sequence[Transaction]:
        """Return all transactions for export."""
        stmt = (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
            .order_by(Transaction.txn_date.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_accounts_balance(
        self, user_id: uuid.UUID
    ) -> Sequence[Account]:
        """Return all accounts for balance-check alert logic."""
        stmt = select(Account).where(Account.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
