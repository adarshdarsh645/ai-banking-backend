import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category_rule import CategoryRule
from app.repositories.category_rule_repository import CategoryRuleRepository


class RuleEngine:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = CategoryRuleRepository(session)

    async def fetch_rules(self, user_id: uuid.UUID) -> list[CategoryRule]:
        # Fetch and cache rules in memory for the request lifecycle,
        # ordered by priority: exact(1) > partial(2) > keyword(3)
        rules = await self._repo.get_user_rules(user_id)
        
        def priority(r: CategoryRule) -> int:
            if r.match_type == "exact": return 1
            if r.match_type == "partial": return 2
            if r.match_type == "keyword": return 3
            return 4
            
        return sorted(rules, key=priority)

    def evaluate(self, merchant: str | None, rules: list[CategoryRule]) -> str | None:
        if not merchant:
            return None
            
        merchant_lower = merchant.lower()
        
        for rule in rules:
            pattern_lower = rule.merchant_pattern.lower()
            if rule.match_type == "exact" and merchant_lower == pattern_lower:
                return rule.category
            elif rule.match_type == "partial" and pattern_lower in merchant_lower:
                return rule.category
            elif rule.match_type == "keyword":
                # Keyword: token match
                tokens = set(merchant_lower.split())
                if pattern_lower in tokens:
                    return rule.category
        
        return None

    async def auto_categorize(self, user_id: uuid.UUID, merchant: str | None) -> str:
        rules = await self.fetch_rules(user_id)
        category = self.evaluate(merchant, rules)
        return category if category else "Uncategorized"

    async def create_rule(
        self, user_id: uuid.UUID, merchant_pattern: str, match_type: str, category: str
    ) -> CategoryRule:
        return await self._repo.create_rule(
            user_id=user_id,
            merchant_pattern=merchant_pattern,
            match_type=match_type,
            category=category,
        )
