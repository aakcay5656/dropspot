from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WaitlistJoinResponse(BaseModel):
    message: str
    position: int
    priority_score: float

class WaitlistLeaveResponse(BaseModel):
    message: str

class ClaimResponse(BaseModel):
    message: str
    claim_code: str
    expires_at: datetime
