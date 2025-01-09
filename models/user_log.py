from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class UserLog(Base):
    __tablename__ = "user_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)  # Username of the user
    ip_address = Column(String, nullable=True)  # IP address of the user
    user_agent = Column(String, nullable=True)  # User agent of the user's browser
    login_time = Column(DateTime, default=datetime.utcnow)  # Login time in UTC
    india_time = Column(String, nullable=False)  # Login time in Indian Standard Time (IST)
