import csv
import io
import uuid
from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import (
    CSVImportResult,
    TransactionCreate,
    TransactionFilter,
    TransactionListResponse,
    TransactionResponse,
    TransactionRecategorize,
)
from app.services.rule_engine import RuleEngine
from app.services.budget_service import BudgetService

# CSV columns that map to model fields
_CSV_REQUIRED_COLS = {
    "description",
    "amount",
    "txn_type",
    "txn_date",
}
_VALID_TXN_TYPES = {"debit", "credit"}


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._repo = TransactionRepository(session)
        self._account_repo = AccountRepository(session)
        self._rule_engine = RuleEngine(session)
        self._budget_service = BudgetService(session)

    # ─── Ownership guard ───────────────────────────────────────────────────────
    async def _assert_account_ownership(
        self, account_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        account = await self._account_repo.get_user_account_by_id(account_id, user_id)
        if not account:
            raise ForbiddenError("Account does not belong to the current user.")

    # ─── Create ────────────────────────────────────────────────────────────────
    async def create_transaction(
        self, data: TransactionCreate, user_id: uuid.UUID
    ) -> TransactionResponse:
        await self._assert_account_ownership(data.account_id, user_id)
        
        category = data.category
        if category == "Uncategorized":
            category = await self._rule_engine.auto_categorize(user_id, data.merchant)

        txn = await self._repo.create_transaction(
            account_id=data.account_id,
            description=data.description,
            category=category,
            amount=data.amount,
            currency=data.currency,
            txn_type=data.txn_type,
            txn_date=data.txn_date,
            merchant=data.merchant,
            posted_date=data.posted_date,
        )
        
        if txn.txn_type == "debit":
            await self._budget_service.check_budget_and_alert(
                user_id, category, txn.txn_date.month, txn.txn_date.year
            )
            
        return TransactionResponse.model_validate(txn)

    # ─── List with filter + pagination ────────────────────────────────────────
    async def list_transactions(
        self, filters: TransactionFilter, user_id: uuid.UUID
    ) -> TransactionListResponse:
        if filters.account_id:
            await self._assert_account_ownership(filters.account_id, user_id)

        total, txns = await self._repo.get_transactions(
            user_id=user_id,
            account_id=filters.account_id,
            txn_type=filters.txn_type,
            date_from=filters.date_from,
            date_to=filters.date_to,
            page=filters.page,
            page_size=filters.page_size,
        )
        return TransactionListResponse(
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            items=[TransactionResponse.model_validate(t) for t in txns],
        )

    # ─── Get single ───────────────────────────────────────────────────────────
    async def get_transaction(
        self, txn_id: uuid.UUID, user_id: uuid.UUID
    ) -> TransactionResponse:
        txn = await self._repo.get_user_transaction_by_id(txn_id, user_id)
        if not txn:
            raise NotFoundError("Transaction")
        return TransactionResponse.model_validate(txn)

    # ─── Recategorize ─────────────────────────────────────────────────────────
    async def recategorize_transaction(
        self, txn_id: uuid.UUID, data: TransactionRecategorize, user_id: uuid.UUID
    ) -> TransactionResponse:
        txn = await self._repo.get_user_transaction_by_id(txn_id, user_id)
        if not txn:
            raise NotFoundError("Transaction")
            
        old_category = txn.category
        txn = await self._repo.update(txn, category=data.category)
        
        if data.create_rule and txn.merchant:
            await self._rule_engine.create_rule(
                user_id=user_id,
                merchant_pattern=txn.merchant,
                match_type="exact",
                category=data.category
            )
            
        if txn.txn_type == "debit":
            # Recalculate overspending for both old and new category
            await self._budget_service.check_budget_and_alert(
                user_id, old_category, txn.txn_date.month, txn.txn_date.year
            )
            await self._budget_service.check_budget_and_alert(
                user_id, data.category, txn.txn_date.month, txn.txn_date.year
            )
            
        return TransactionResponse.model_validate(txn)

    # ─── CSV Import ───────────────────────────────────────────────────────────
    async def import_csv(
        self,
        account_id: uuid.UUID,
        user_id: uuid.UUID,
        csv_bytes: bytes,
    ) -> CSVImportResult:
        await self._assert_account_ownership(account_id, user_id)

        content = csv_bytes.decode("utf-8-sig")  # handle BOM
        reader = csv.DictReader(io.StringIO(content))

        if not reader.fieldnames:
            return CSVImportResult(imported=0, failed=0, errors=["CSV file is empty."])

        # Normalise column names
        fieldnames = {c.strip().lower() for c in reader.fieldnames}
        missing = _CSV_REQUIRED_COLS - fieldnames
        if missing:
            return CSVImportResult(
                imported=0,
                failed=0,
                errors=[f"Missing required columns: {', '.join(sorted(missing))}"],
            )

        rules = await self._rule_engine.fetch_rules(user_id)
        records: list[dict] = []
        errors: list[str] = []
        categories_to_check = set()

        for row_num, row in enumerate(reader, start=2):
            # Normalise keys
            row = {k.strip().lower(): (v or "").strip() for k, v in row.items()}
            row_errors = _validate_csv_row(row, row_num)
            if row_errors:
                errors.extend(row_errors)
                continue
                
            merchant = row.get("merchant") or None
            category = row.get("category")
            if not category or category == "Uncategorized":
                category = self._rule_engine.evaluate(merchant, rules) or "Uncategorized"
                
            txn_date = _parse_date(row["txn_date"])
            txn_type = row["txn_type"].lower()
            
            records.append(
                {
                    "account_id": account_id,
                    "description": row["description"],
                    "category": category,
                    "amount": Decimal(row["amount"]),
                    "currency": (row.get("currency") or "USD").upper(),
                    "txn_type": txn_type,
                    "merchant": merchant,
                    "txn_date": txn_date,
                    "posted_date": _parse_date(row["posted_date"])
                    if row.get("posted_date")
                    else None,
                }
            )
            
            if txn_type == "debit":
                categories_to_check.add((category, txn_date.month, txn_date.year))

        imported = 0
        if records:
            imported = await self._repo.bulk_create(records)
            for cat, mo, yr in categories_to_check:
                await self._budget_service.check_budget_and_alert(user_id, cat, mo, yr)

        return CSVImportResult(
            imported=imported,
            failed=len(errors),
            errors=errors,
        )


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _validate_csv_row(row: dict, row_num: int) -> list[str]:
    errs: list[str] = []
    if not row.get("description"):
        errs.append(f"Row {row_num}: 'description' is required.")
    if not row.get("amount"):
        errs.append(f"Row {row_num}: 'amount' is required.")
    else:
        try:
            val = Decimal(row["amount"])
            if val <= 0:
                errs.append(f"Row {row_num}: 'amount' must be positive.")
        except InvalidOperation:
            errs.append(f"Row {row_num}: 'amount' is not a valid number.")
    txn_type = row.get("txn_type", "").lower()
    if txn_type not in _VALID_TXN_TYPES:
        errs.append(
            f"Row {row_num}: 'txn_type' must be one of {sorted(_VALID_TXN_TYPES)}, got '{txn_type}'."
        )
    if not row.get("txn_date"):
        errs.append(f"Row {row_num}: 'txn_date' is required.")
    else:
        try:
            _parse_date(row["txn_date"])
        except ValueError:
            errs.append(
                f"Row {row_num}: 'txn_date' must be in YYYY-MM-DD format, got '{row['txn_date']}'."
            )
    return errs


def _parse_date(value: str) -> date:
    return date.fromisoformat(value.strip())
