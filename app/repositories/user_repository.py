import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        user = await self.get_by_email(email)
        return user is not None

    async def create_user(
        self,
        name: str,
        email: str,
        hashed_password: str,
        phone: str | None = None,
    ) -> User:
        return await self.create(
            name=name,
            email=email,
            hashed_password=hashed_password,
            phone=phone,
        )

    async def get_all_users(self) -> list[User]:
        stmt = select(User)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
