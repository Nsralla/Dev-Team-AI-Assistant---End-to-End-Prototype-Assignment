# create_db.py
from sqlalchemy import create_engine
from models import Base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///data/data_store.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)
