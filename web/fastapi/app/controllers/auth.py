from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import EmailStr
import os
from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse


from models import User, get_db
from schemas.user_schemas import UserCreate, UserLogin, UserOut, Token

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 사용자 이름 또는 이메일 중복 확인
    existing_user = db.query(User).filter(
        (User.userName == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # 비밀번호 해싱
    hashed_password = get_password_hash(user.password)
    new_user = User(
        userName=user.username,
        email=user.email,
        passWordHash=hashed_password,
        fullName=user.fullname,
        gender=user.gender,
        birthdate=user.birthdate,
        phone=user.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserOut(id=new_user.id, username=new_user.userName, email=new_user.email)

@router.post("/signup-form", response_class=HTMLResponse)
def signup_form(
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    fullname: str = Form(...),
    gender: str = Form(...),
    birthdate: date = Form(...),
    phone: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        user_create = UserCreate(
            username=username,
            email=email,
            password=password,
            fullname=fullname,
            gender=gender,
            birthdate=birthdate,
            phone=phone
        )
        create_user(user_create, db)
        # 성공 시 기본 페이지로 리디렉션
        return RedirectResponse(url="/", status_code=303)
    except HTTPException as e:
        # 오류 시 오류 페이지 또는 현재 페이지로 리디렉션
        return RedirectResponse(url="/signup?error=" + e.detail, status_code=303)

@router.post("/login", response_model=Token)
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.userName == username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(password, db_user.passWordHash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.userName}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-form")
def login_form(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.userName == username).first()
    if not db_user:
        return RedirectResponse(url="/login?error=Incorrect+username+or+password", status_code=303)
    if not verify_password(password, db_user.passWordHash):
        return RedirectResponse(url="/login?error=Incorrect+username+or+password", status_code=303)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.userName}, expires_delta=access_token_expires
    )
    # 로그인 성공 후 세션이나 쿠키 설정 필요시 추가 (예: JWT를 쿠키에 저장)
    
    # 성공 시 기본 페이지로 리디렉션
    return RedirectResponse(url="/", status_code=303)