# create_tables.py
from postgre import Base, engine
import models  # important: ensures Book is registered


Base.metadata.create_all(bind=engine)
print("Tables created!")