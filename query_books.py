from database import SessionLocal
from models import Book

# Create a session
session = SessionLocal()

# Get all books
print("==== All Books ====")
all_books = session.query(Book).all()
for book in all_books:
    print(f"{book.title} by {book.author}")

# Close the session
session.close()
