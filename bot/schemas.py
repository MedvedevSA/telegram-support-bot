from typing import Annotated
from datetime import datetime

from pydantic import BaseModel

UserId = Annotated[int, "UserId"]

class BotData(BaseModel):
    recent_user_activity: dict[UserId, Annotated[datetime, 'MessageDate']]
