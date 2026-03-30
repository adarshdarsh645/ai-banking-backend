import uuid
from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    user_id: uuid.UUID
    alert_type: str
    message: str
    category: str | None
    month: int | None
    year: int | None
    is_read: bool
    created_at: datetime
