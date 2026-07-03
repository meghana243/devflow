from crypto import hash_password

from database import SessionLocal
from models import Book

db = SessionLocal()
db.add(Book(title="The Great Gatsby", author="F. Scott Fitzgerald",hashed_password=hash_password("secret123")))
db.commit()
db.close()
