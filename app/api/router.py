from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.accounts import router as accounts_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.budgets import router as budgets_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.reports import router as reports_router
from app.api.routes.bills import router as bills_router
from app.api.routes.rewards import router as rewards_router
from app.api.routes.currency import router as currency_router
from app.api.routes.insights import router as insights_router
from app.api.routes.export import router as export_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(accounts_router)
api_router.include_router(transactions_router)
api_router.include_router(budgets_router)
api_router.include_router(alerts_router)
api_router.include_router(reports_router)
api_router.include_router(bills_router)
api_router.include_router(rewards_router)
api_router.include_router(currency_router)
api_router.include_router(insights_router)
api_router.include_router(export_router)
