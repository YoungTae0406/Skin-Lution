from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import uuid

app = FastAPI()

# sqlite3 db와 연결하는 함수
def connectDB():
    # user.db 파일이 존재하지 않는단면, sqlite가 자동으로 파일을 생성함.
    conn = sqlite3.connect('users.db')
    # db에서 조회한 결과를 다루는 방식 설정. 
    # 쿼리 결과를 row 객체로 반환하여, 열 이름을 통해 접근할 수 있게 함.
    conn.row_factory = sqlite3.Row
    return conn

# User table을 만드는 함수
def createUserTables():
    conn = connectDB()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            userName TEXT NOT NULL,
            passWordHash TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            lastLogin TEXT,
            skinType TEXT
        )
    ''')
    conn.commit()
    conn.close()


# docs에서 확인가능
@app.get("/")
def read_root():
    return {"Hello": "World"}
