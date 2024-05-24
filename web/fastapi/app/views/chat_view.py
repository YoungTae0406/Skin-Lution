from fastapi import APIRouter
from controllers import chat

router = APIRouter()

# /chat 경로에 chat 컨트롤러의 라우터를 포함
router.include_router(chat.router, prefix="/chat")