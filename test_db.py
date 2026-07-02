from database import SessionLocal
from models import Book

db = SessionLocal()
db.add(Book(title="The Great Gatsby", author="F. Scott Fitzgerald"))
db.commit()
db.close()
