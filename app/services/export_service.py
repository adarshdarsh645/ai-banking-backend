"""
export_service.py — CSV and simple text-based PDF export.
Uses stdlib csv and reportlab if available, else plain text fallback for PDF.
"""
import csv
import io
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.budget_repository import BudgetRepository
from app.repositories.insights_repository import InsightsRepository


class ExportService:
    def __init__(self, session: AsyncSession) -> None:
        self._insights = InsightsRepository(session)
        self._budgets = BudgetRepository(session)

    async def export_transactions_csv(self, user_id: uuid.UUID) -> bytes:
        transactions = await self._insights.get_all_transactions(user_id)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "account_id", "description", "category",
            "amount", "currency", "txn_type", "merchant",
            "txn_date", "created_at"
        ])
        for t in transactions:
            writer.writerow([
                str(t.id), str(t.account_id), t.description, t.category,
                t.amount, t.currency, t.txn_type, t.merchant or "",
                t.txn_date.isoformat(), t.created_at.isoformat()
            ])

        return output.getvalue().encode("utf-8")

    async def export_insights_pdf(self, user_id: uuid.UUID) -> bytes:
        """Generate a simple plaintext report as PDF-like bytes."""
        transactions = await self._insights.get_all_transactions(user_id)
        category_rows = await self._insights.get_category_spend(user_id)
        budgets = await self._budgets.get_user_budgets(user_id)

        lines = []
        lines.append("=== AI Banking — Insights Report ===\n")
        lines.append(f"Total Transactions: {len(transactions)}\n")
        lines.append("\n--- Spending by Category ---\n")
        for r in category_rows:
            lines.append(f"  {r.category}: {r.total}\n")
        lines.append("\n--- Budgets ---\n")
        for b in budgets:
            lines.append(f"  {b.category} ({b.month}/{b.year}): limit={b.amount_limit}\n")

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=letter)
            c.setFont("Helvetica", 12)
            y = 750
            for line in lines:
                c.drawString(50, y, line.strip())
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 750
            c.save()
            buf.seek(0)
            return buf.read()

        except ImportError:
            # Fallback if reportlab not installed: return plain text
            return "".join(lines).encode("utf-8")
