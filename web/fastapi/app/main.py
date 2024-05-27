from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi import Request

from views import chat_view

app = FastAPI()

# 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="/app/views/static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="/app/views/templates")

# fastapi에 router를 포함시킨다. 
# chat_view에서 정의된 라우터를 메인 애플리케이션에 포함.
app.include_router(chat_view.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})