# 비즈니스 로직 처리
import sqlite3
from hashlib import sha256
from models import connectDB


def hashPassword(password: str) -> str:
    return sha256(password.encode('utf-8')).hexdigest()

def createUser(username: str, password: str):
    conn = connectDB()
    cursor = conn.cursor()
    password_hash = hashPassword(password)
    cursor.execute('''
        INSERT INTO users (username, password_hash) VALUES (?, ?)
    ''', (username, password_hash))
    conn.commit()
    conn.close()

def getUser(username: str):
    conn = connectDB()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

'''
from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
from ..database import SessionLocal
from hashlib import sha256

def hashPassword(password: str) -> str:
    return sha256(password.encode('utf-8')).hexdigest()

def createUser(db: Session, user: UserCreate):
    password_hash = hashPassword(user.password)
    db_user = User(username=user.username, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def getUser(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
'''