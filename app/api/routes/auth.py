from fastapi import APIRouter

from app.api.deps import DBSession
from app.schemas.auth import LoginRequest, RefreshTokenRequest, SignupRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.api.deps import CurrentUser

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=201,
    summary="Register a new user",
)
async def signup(payload: SignupRequest, session: DBSession) -> TokenResponse:
    """
    Register a new user account and return JWT access + refresh tokens.
    """
    service = AuthService(session)
    return await service.signup(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user",
)
async def login(payload: LoginRequest, session: DBSession) -> TokenResponse:
    """
    Authenticate with email + password and receive JWT tokens.
    """
    service = AuthService(session)
    return await service.login(payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    payload: RefreshTokenRequest, session: DBSession
) -> TokenResponse:
    """
    Use a valid refresh token to obtain a new access token.
    """
    service = AuthService(session)
    return await service.refresh(payload.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """
    Returns the profile of the currently authenticated user.
    """
    return UserResponse.model_validate(current_user)
