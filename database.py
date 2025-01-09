from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlitecloud://cepdfj5nhk.sqlite.cloud:8860/sales-database-09-dev?apikey=pKH2wzPEGoQzkA5JlVg2vCS8msEsbtdJPwshboDfaYw"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()