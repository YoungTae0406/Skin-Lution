from fastapi import APIRouter, HTTPException
#from models.model import get_chat_response
from models.gptmodel import chat_gpt_model
from schemas.chat_schemas import ChatResponse, ChatRequest

router = APIRouter()
'''
@router.post("/", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    try:
        response_data = chat_gpt_model.get_response(request.user_input)
        # get_chat_response는 ai와 연결될 함수
        bot_response = get_chat_response(request.user_input)
        return ChatResponse(bot_response=bot_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
