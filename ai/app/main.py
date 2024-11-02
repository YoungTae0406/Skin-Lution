# main.py

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.memory import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_models import ChatOpenAI
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, CSVLoader
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
import nltk
import re

app = FastAPI()

class ChatRequest(BaseModel):
    user_message: str

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

def set_api_keys():
    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGCHAIN_API_KEY")

# API 키 설정 호출
set_api_keys()

def load_documents(data_path: str):
    documents = {}
    
    pdf_loader = DirectoryLoader(".", glob=f"{data_path}/thesis/*.pdf", show_progress=True)
    documents['pdf_docs'] = pdf_loader.load()
    
    txt_loader = DirectoryLoader(".", glob=f"{data_path}/skincare/*.txt", show_progress=True)
    documents['txt_docs'] = txt_loader.load()
    
    csv_loader = CSVLoader(file_path=f"{data_path}/cosmetics/화장품데이터.csv", encoding='utf-8')
    documents['csv_docs'] = csv_loader.load()
    return documents

def split_documents(documents, chunk_size=500, chunk_overlap=100, add_start_index=True):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=add_start_index
    )
    return splitter.split_documents(documents)


# FAISS vectorstore 로드 시 역직렬화 허용 추가
def load_or_create_vectorstore(documents, file_path):
    if os.path.exists(file_path):
        # allow_dangerous_deserialization=True 추가
        return FAISS.load_local(file_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    else:
        vectorstore = create_vectorstore(documents)
        vectorstore.save_local(file_path)
        return vectorstore

def create_vectorstore(documents, embedding_model=None):
    embedding_model = embedding_model or OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents=documents, embedding=embedding_model)
    return vectorstore

def merge_vectorstores(primary_store, secondary_store):
    primary_store.merge_from(secondary_store)

def initialize():
    data_path = "./data"
    docs = load_documents(data_path)

    pdf_splits = split_documents(docs['pdf_docs'], chunk_size=500, chunk_overlap=100)
    txt_splits = split_documents(docs['txt_docs'], chunk_size=300, chunk_overlap=50)

    pdf_vectorstore = load_or_create_vectorstore(pdf_splits, "./vectorstore/pdf_vectorstore")
    txt_vectorstore = load_or_create_vectorstore(txt_splits, "./vectorstore/txt_vectorstore")
    cosmetic_vectorstore = load_or_create_vectorstore(docs['csv_docs'], "./vectorstore/cosmetic_vectorstore")

    # PDF와 TXT 벡터 스토어 병합
    merge_vectorstores(pdf_vectorstore, txt_vectorstore)

    # 리트리버 생성
    retriever1 = pdf_vectorstore.as_retriever(k=3)
    retriever2 = cosmetic_vectorstore.as_retriever(k=50)

    return retriever1, retriever2

# 리트리버 초기화
retriever1, retriever2 = initialize()

# GPT LLM 생성
llm = ChatOpenAI(
    temperature=0,  # 창의성 (0.0 ~ 2.0) 낮을수록 같은 질문에 같은 대답
    model_name="gpt-4o-mini",  # 모델명 (실제 사용 가능한 모델로 변경)
)

def is_cosmetic_query(user_message):
    # 간단한 키워드 기반 분류기
    cosmetic_keywords = ["화장품", "제품", "스킨케어", "로션", "크림"]
    return any(keyword in user_message for keyword in cosmetic_keywords)
                             
def select_vectorstore(user_message):
    if is_cosmetic_query(user_message):
        return retriever2
    else:
        return retriever1

# def perform_retrieval(user_message):
#     selected_retriever = select_retriever(user_message)
#     # 질의 변환 및 검색 수행
#     query_transform_prompt = ChatPromptTemplate.from_messages(
#         [
#             MessagesPlaceholder(variable_name="messages"),
#             (
#                 "user",
#                 "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
#             ),
#         ]
#     )

#     question_answering_prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 "Answer the user's question based on the below context:\n\n{context}",
#             ),
#             MessagesPlaceholder(variable_name="messages"),
#         ]
#     )

#     query_transforming_retriever_chain = RunnableBranch(
#         (
#             lambda x: len(x.get("messages", [])) == 1,
#             (lambda x: x["messages"][-1].content) | selected_retriever,
#         ),
#         query_transform_prompt 
#         | llm 
#         | StrOutputParser() 
#         | selected_retriever,
#     ).with_config(run_name="chat_retriever_chain")

#     document_chain = create_stuff_documents_chain(llm, question_answering_prompt)

#     conversational_retrieval_chain = RunnablePassthrough.assign(
#         context=query_transforming_retriever_chain,
#     ).assign(
#         answer=document_chain,
#     )
#     return conversational_retrieval_chain

def perform_retrieval(user_message, messages):
    selected_vectorstore = select_vectorstore(user_message)
    
    # 질의 변환 및 검색 수행
    query_transform_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            (
                "user",
                "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
            ),
        ]
    )

    question_answering_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the user's question based on the below context:\n\n{context}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    query_transforming_retriever_chain = RunnableBranch(
        (
            lambda x: len(x.get("messages", [])) == 1,
            (lambda x: x["messages"][-1].content) | selected_vectorstore,
        ),
        query_transform_prompt 
        | llm 
        | StrOutputParser() 
        | selected_vectorstore,
    ).with_config(run_name="chat_retriever_chain")

    document_chain = create_stuff_documents_chain(llm, question_answering_prompt)

    conversational_retrieval_chain = RunnablePassthrough.assign(
        context=query_transforming_retriever_chain,
    ).assign(
        answer=document_chain,
    )
    
    # 검색 체인에 messages를 전달하여 결과 반환
    return conversational_retrieval_chain.invoke({"messages": messages})


def extract_document_info(response):
    if "context" in response and response["context"]:
        first_document = response["context"][0]
        title = first_document.page_content.split('\n')[0].strip()
        metadata = first_document.metadata
        return title, metadata
    return None, None

def display_ai_messages(chat_history, printed_messages):
    ai_messages = [msg.content for msg in chat_history.messages if isinstance(msg, AIMessage)]
    for msg in ai_messages:
        if msg not in printed_messages:
            print(msg)
            printed_messages.append(msg)

def display_document_metadata(metadata):
    metadata_text = ""
    for key, value in metadata.items():
        if key == "source":
            match = re.search(r'\\(.+?)\s-\s', value)
            if match:
                value = match.group(1)
            metadata_text += f"답변에 활용한 정보: {value}\n"
    return metadata_text.strip() if metadata_text else None

'''
@app.post("/chat")
async def chat_api(user_message: str = Form(...)):
    try:
        # Initialize chat history for the session
        chat_history = ChatMessageHistory()
        chat_history.add_user_message(user_message)
        
        # Perform retrieval and get the response
        response = perform_retrieval(user_message, chat_history.messages)

        # Extract the AI response and update chat history
        chat_history.add_ai_message(response["answer"])

        # Extract document title and metadata if available
        first_document_title, first_document_metadata = extract_document_info(response)

        # Format metadata for response
        metadata_text = display_document_metadata(first_document_metadata) if first_document_metadata else None

        # Return response as JSON
        return JSONResponse({
            "ai_message": response["answer"],
            "document_title": first_document_title,
            "document_metadata": metadata_text
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

@app.post("/chat")
async def chat_api(request: ChatRequest):
    user_message = request.user_message
    try:
        # Initialize chat history for the session
        chat_history = ChatMessageHistory()
        chat_history.add_user_message(user_message)

        # Perform retrieval and get the response
        response = perform_retrieval(user_message, chat_history.messages)

        # Extract the AI response and update chat history
        chat_history.add_ai_message(response["answer"])

        # Extract document title and metadata if available
        first_document_title, first_document_metadata = extract_document_info(response)

        # Format metadata for response
        metadata_text = display_document_metadata(first_document_metadata) if first_document_metadata else None

        # Return response as JSON
        return JSONResponse({
            "ai_message": response["answer"],
            "document_title": first_document_title,
            "document_metadata": metadata_text
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

