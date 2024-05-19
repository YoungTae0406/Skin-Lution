from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import UserCreate, UserResponse
from ..controllers.user import createUser, getUser
from ..database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = getUser(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return createUser(db, user)

@router.get("/users/{username}", response_model=UserResponse)
def read_user(username: str, db: Session = Depends(get_db)):
    db_user = getUser(db, username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not