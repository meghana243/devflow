
from sqlalchemy import Column, Integer, String
from postgre import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)  # New field for hashed password
