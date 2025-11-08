from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ClaimCode(Base):
    __tablename__ = "claim_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    waitlist_id = Column(Integer, ForeignKey("waitlist.id", ondelete="CASCADE"), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
