from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid
import database.py

app = FastAPI()

# docs에서 확인가능
@app.get("/")
def read_root():
    return {"Hello": "World"}
