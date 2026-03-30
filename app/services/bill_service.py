import uuid
from datetime import date, timedelta
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.bill import Bill
from app.repositories.bill_repository import BillRepository
from app.schemas.bill import BillCreate, BillResponse, BillUpdate
from app.services.alert_service import AlertService


class BillService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._repo = BillRepository(session)
        self._alert_service = AlertService(session)

    async def _update_status_if_needed(self, bill: Bill, today: date) -> bool:
        """Autoupdates the bill status based on the due date. Returns True if updated."""
        if bill.status == "paid":
            return False

        new_status = "upcoming"
        if today > bill.due_date:
            new_status = "overdue"

        if bill.status != new_status:
            bill.status = new_status
            return True
        return False

    async def create_bill(self, user_id: uuid.UUID, data: BillCreate) -> BillResponse:
        bill = await self._repo.create(
            user_id=user_id,
            biller_name=data.biller_name,
            due_date=data.due_date,
            amount_due=data.amount_due,
            auto_pay=data.auto_pay,
            status="upcoming",
        )
        today = date.today()
        if await self._update_status_if_needed(bill, today):
            await self.session.flush()

        return BillResponse.model_validate(bill)

    async def get_user_bills(self, user_id: uuid.UUID) -> list[BillResponse]:
        bills = await self._repo.get_user_bills(user_id)
        today = date.today()
        updated = False
        
        for bill in bills:
            if await self._update_status_if_needed(bill, today):
                updated = True
                
        if updated:
            await self.session.flush()

        return [BillResponse.model_validate(b) for b in bills]

    async def get_bill(self, bill_id: uuid.UUID, user_id: uuid.UUID) -> BillResponse:
        bill = await self._repo.get_user_bill(bill_id, user_id)
        if not bill:
            raise NotFoundError("Bill")

        today = date.today()
        if await self._update_status_if_needed(bill, today):
            await self.session.flush()

        return BillResponse.model_validate(bill)

    async def update_bill(
        self, bill_id: uuid.UUID, user_id: uuid.UUID, data: BillUpdate
    ) -> BillResponse:
        bill = await self._repo.get_user_bill(bill_id, user_id)
        if not bill:
            raise NotFoundError("Bill")

        update_data = data.model_dump(exclude_unset=True)
        bill = await self._repo.update(bill, **update_data)

        # Force status recalculation if status was not manually set to paid in this update
        today = date.today()
        if await self._update_status_if_needed(bill, today):
            pass # already tracked

        return BillResponse.model_validate(bill)

    async def delete_bill(self, bill_id: uuid.UUID, user_id: uuid.UUID) -> None:
        bill = await self._repo.get_user_bill(bill_id, user_id)
        if not bill:
            raise NotFoundError("Bill")
        await self._repo.delete(bill)

    async def process_reminders(self) -> int:
        """Finds bills due in next 2 days and creates alerts."""
        today = date.today()
        max_due = today + timedelta(days=2)
        
        bills = await self._repo.get_upcoming_bills_for_all_users(max_due)
        alerts_created = 0
        
        for bill in bills:
            # We use month/year from due_date for unique key constraint.
            # So alert deduplicates automatically per month
            message = f"Reminder: Bill for {bill.biller_name} amount {bill.amount_due} is due on {bill.due_date}."
            alert = await self._alert_service._repo.create_alert_if_not_exists(
                user_id=bill.user_id,
                alert_type="bill_due",
                message=message,
                category=bill.biller_name,
                month=bill.due_date.month,
                year=bill.due_date.year,
            )
            if alert:
                alerts_created += 1
                
        if alerts_created > 0:
            await self.session.flush()
            
        return alerts_created
