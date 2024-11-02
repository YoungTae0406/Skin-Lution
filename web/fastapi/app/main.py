from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from datetime import timedelta

from models import initDB
from controllers import auth_router

app = FastAPI()

origins = [
    "http://localhost:8000",  # AI Chat 애플리케이션이 실행되는 출처
    "http://localhost:8888"  # 웹페이지가 실행되는 출처 (예시)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="/app/views/static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="/app/views/templates")

#app.include_router(chat_view.router)
app.include_router(auth_router)

# 채팅 페이지 라우트
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# 로그인 페이지 라우트
@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 회원가입 페이지 라우트
@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})