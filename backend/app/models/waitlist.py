from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class WaitlistStatus(str, enum.Enum):
    WAITING = "waiting"
    CLAIMED = "claimed"
    EXPIRED = "expired"


class Waitlist(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, index=True)
    drop_id = Column(Integer, ForeignKey("drops.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Priority score calculation
    priority_score = Column(Float, nullable=False, index=True)
    signup_latency_ms = Column(Integer)
    account_age_days = Column(Integer)
    rapid_actions_count = Column(Integer, default=0)

    # Status
    status = Column(Enum(WaitlistStatus), default=WaitlistStatus.WAITING, nullable=False, index=True)
    claim_code = Column(String(255), unique=True)
    claimed_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="waitlist_entries")
    drop = relationship("Drop", back_populates="waitlist_entries")

    # Unique constraint: user can only join a drop once
    __table_args__ = (
        UniqueConstraint('drop_id', 'user_id', name='_drop_user_uc'),
        Index('idx_drop_priority', 'drop_id', 'priority_score'),
    )
