from sqlalchemy import Column, Integer, String
from database import Base

class Book(Base):
    __tablename__="books"

    id=Column(Integer, primary_key=True, index=True)
    title=Column(String, index=True)
    author=Column(String, index=True)

    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}')>"