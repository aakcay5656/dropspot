from sqlalchemy import Column,Integer,String,DateTime,Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class UserRole(str,enum.Enum):
    USER = 'user'
    ADMIN = 'admin'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True,index=True)
    email = Column(String(255),unique=True,nullable=False,index=True)
    password = Column(String(255),nullable=False)
    role = Column(Enum(UserRole),default=UserRole.USER,nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships

    waitlist_entries = relationship('Waitlist',back_populates='user')
    created_drops = relationship("Drop",back_populates="creator")



