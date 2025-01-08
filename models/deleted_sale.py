from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from database import Base

class DeletedSale(Base):
    __tablename__ = "deleted_sales"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    product_description = Column(String, nullable=True)
    supplier_name = Column(String, index=True)
    order_datetime = Column(DateTime)
    sale_price = Column(Float)
    amazon_commission = Column(Float)
    quantity = Column(Integer)
    buy_price = Column(Float)
    estimated_delivery = Column(Date)
    sale_date = Column(Date)
    buyer_name = Column(String, index=True)
    buyer_address = Column(String, nullable=True)
    delivery_status = Column(String, nullable=True)
    manage_link = Column(String, nullable=True)
    amazon_link = Column(String, nullable=True)
    payment_link = Column(String, nullable=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    forex_fees = Column(Float, nullable=True)
