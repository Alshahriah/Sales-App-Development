from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class CRUDLog(Base):
    __tablename__ = "crud_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)  # e.g., CREATE, READ, UPDATE, DELETE
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = Column(String, nullable=True)
    record_id = Column(Integer)
    model = Column(String)  # The model affected, e.g., Sale
    details = Column(String, nullable=True)  # Optional field to store additional details
