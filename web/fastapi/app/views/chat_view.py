from fastapi import APIRouter
from app.controllers import consultation

router = APIRouter()

# /consultation 경로에 consultation 컨트롤러의 라우터를 포함
router.include_router(consultation.router, prefix="/chat")