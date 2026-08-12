import os
from sqlmodel import Session, create_engine
from dotenv import load_dotenv
 
load_dotenv()
 
DATABASE_URL = os.getenv("RPi_DATABASE_URL")
 
if DATABASE_URL is None:
    raise RuntimeError("RPi_DATABASE_URL is missing. Check your .env file.")
 
engine = create_engine(DATABASE_URL, echo=True)