from pydantic import BaseModel
# pydantic -> 데이터 유효성 검사 및 설정을 위해 사용하는 라이브러리.
# API의 입력과 출력을 정의하고 자동으로 데이터 유효성 검사를 수행함. 
# 데이터 직렬화 및 역직렬화의 기능도 존재하고, API 문서를 자동으로 생성해줌.

class ChatRequest(BaseModel):
    user_id: int # 고민해봐야됨.
    user_input: str

class ChatResponse(BaseModel):
    bot_response: str