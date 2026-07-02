# main.py
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from models import Book
from postgre import get_db
from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str

class BookResponse(BaseModel):
    id: int
    title: str
    author: str

app = FastAPI()

@app.post("/books/")
def create_book(item: BookCreate, db: Session = Depends(get_db)):
    book = Book(title=item.title, author=item.author)
    db.add(book)
    db.commit()
    db.refresh(book)
    return BookResponse(id=book.id, title=book.title, author=book.author)

@app.get("/books/{book_id}")
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    return BookResponse(id=book.id, title=book.title, author=book.author)
