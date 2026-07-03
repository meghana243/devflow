from datetime import timedelta, datetime
from jose import jwt
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Book
from postgre import get_db
from crypto import verify_password   # import from your crypto.py

app = FastAPI()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta):
    return jwt.encode(
        {**data, "exp": datetime.utcnow() + expires_delta},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

@app.post("/token")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(Book).filter(Book.title == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token({"sub": user.title}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}
