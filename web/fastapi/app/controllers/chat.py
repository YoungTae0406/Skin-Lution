from fastapi import APIRouter, HTTPException
#from models.model import get_chat_response
from schemas.chat_schemas import ChatResponse, ChatRequest

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    try:
        # get_chat_response는 ai와 연결될 함수
        bot_response = get_chat_response(request.user_input)
        return ChatResponse(bot_response=bot_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))