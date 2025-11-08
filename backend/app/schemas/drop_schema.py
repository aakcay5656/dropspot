from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DropCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    total_stock: int = Field(..., gt=0)
    claim_window_start: datetime
    claim_window_end: datetime


class DropUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    total_stock: Optional[int] = Field(None, gt=0)
    claim_window_start: Optional[datetime] = None
    claim_window_end: Optional[datetime] = None
    status: Optional[str] = None


class DropResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    total_stock: int
    claimed_count: int
    claim_window_start: datetime
    claim_window_end: datetime
    status: str
    created_at: datetime
    user_joined: bool = False

    class Config:
        from_attributes = True
