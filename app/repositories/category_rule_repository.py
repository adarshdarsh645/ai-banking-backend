import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category_rule import CategoryRule
from app.repositories.base import BaseRepository


class CategoryRuleRepository(BaseRepository[CategoryRule]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(CategoryRule, session)

    async def get_user_rules(self, user_id: uuid.UUID) -> Sequence[CategoryRule]:
        # Sort so that exact > partial > keyword isn't strictly needed in query if handled by engine,
        # but returning them sorted by priority helps.
        # Priority map: exact=1, partial=2, keyword=3.
        # We can just fetch all for the user and let the service sort/evaluate them.
        stmt = select(CategoryRule).where(CategoryRule.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_rule(
        self,
        user_id: uuid.UUID,
        merchant_pattern: str,
        match_type: str,
        category: str,
    ) -> CategoryRule:
        rule = await self.create(
            user_id=user_id,
            merchant_pattern=merchant_pattern,
            match_type=match_type,
            category=category,
        )
        return rule
