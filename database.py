from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///example.db', echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



