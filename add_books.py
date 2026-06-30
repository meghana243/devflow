from database import SessionLocal
from models import Book

book=[
    Book(title="1984", author="George Orwell"),
    Book(title="To Kill a Mockingbird", author="Harper Lee")   
]

session=SessionLocal()
session.add_all(book)
session.commit()
for b in book:
    print(f"Added book: {b.title} by {b.author}")

session.close()

