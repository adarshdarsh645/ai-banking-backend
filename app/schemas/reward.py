import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RewardUpdate(BaseModel):
    points_balance: int = Field(..., ge=0)


class RewardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    program_name: str
    points_balance: int
    created_at: datetime
