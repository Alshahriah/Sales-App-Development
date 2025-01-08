from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlitecloud://cepdfj5nhk.sqlite.cloud:8860/sales-database-09-dev?apikey=pKH2wzPEGoQzkA5JlVg2vCS8msEsbtdJPwshboDfaYw"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    product_description = Column(String, nullable=True)
    supplier_name = Column(String, index=True)
    order_datetime = Column(DateTime, default=datetime.utcnow)
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
    region_id = Column(Integer)
    forex_fees = Column(Float, nullable=True)

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
    region_id = Column(Integer)
    forex_fees = Column(Float, nullable=True)

# Create the tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Manually create deleted_sales table if it doesn't exist
def create_deleted_sales_table():
    conn = engine.connect()
    if not engine.dialect.has_table(engine, "deleted_sales"):
        conn.execute("""
        CREATE TABLE deleted_sales (
            id INTEGER PRIMARY KEY,
            product_name TEXT,
            product_description TEXT,
            supplier_name TEXT,
            order_datetime DATETIME,
            sale_price FLOAT,
            amazon_commission FLOAT,
            quantity INTEGER,
            buy_price FLOAT,
            estimated_delivery DATE,
            sale_date DATE,
            buyer_name TEXT,
            buyer_address TEXT,
            delivery_status TEXT,
            manage_link TEXT,
            amazon_link TEXT,
            payment_link TEXT,
            region_id INTEGER,
            forex_fees FLOAT
        );
        """)
    conn.close()

if __name__ == "__main__":
    init_db()
    create_deleted_sales_table()
