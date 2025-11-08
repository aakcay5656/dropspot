from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class DropStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Drop(Base):
    __tablename__ = "drops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    total_stock = Column(Integer, nullable=False)
    claimed_count = Column(Integer, default=0, nullable=False)

    # Zaman bilgisi
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    claim_window_start = Column(DateTime, nullable=False)
    claim_window_end = Column(DateTime, nullable=False)

    # Admin
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(DropStatus), default=DropStatus.ACTIVE, nullable=False, index=True)

    # Relationships
    creator = relationship("User", back_populates="created_drops")
    waitlist_entries = relationship("Waitlist", back_populates="drop", cascade="all, delete-orphan")
