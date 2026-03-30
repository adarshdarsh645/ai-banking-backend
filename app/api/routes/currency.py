from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.report import CurrencyRatesResponse
from app.services.currency_service import CurrencyService

router = APIRouter(prefix="/currency-rates", tags=["Currency"])


@router.get(
    "",
    response_model=CurrencyRatesResponse,
    summary="Get major currency exchange rates",
)
async def get_currency_rates(
    current_user: CurrentUser,  # Protect the endpoint using JWT auth
) -> CurrencyRatesResponse:
    # Service uses synchronous urllib but it's okay for minimal usage and is cached
    rates = CurrencyService.get_rates()
    return CurrencyRatesResponse(**rates)
