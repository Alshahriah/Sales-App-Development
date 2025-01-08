from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Region(Base):
    __tablename__ = 'regions'
    
    id = Column(Integer, primary_key=True, index=True)
    region_name = Column(String, unique=True, nullable=False)
    region_code = Column(String, unique=True, nullable=False)

    # Define relationship with Sale
    sales = relationship("Sale", back_populates="region")
