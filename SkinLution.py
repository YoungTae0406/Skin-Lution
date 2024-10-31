#!/usr/bin/env python
# coding: utf-8

# In[ ]:


pip install sentence-transformers


# In[1]:


from langchain.memory import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import getpass
import os
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import bs4
from langchain.vectorstores import Chroma, FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader
from langchain_community.document_loaders import CSVLoader
from langchain_core.prompts import PromptTemplate
from langchain import hub
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
import os
from langchain.chat_models import ChatOpenAI


# In[4]:


def set_api_keys():
    os.environ["OPENAI_API_KEY"] = ""
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGCHAIN_API_KEY")

# API 키 설정 호출
set_api_keys()


# In[6]:


def load_documents(data_path: str):
    documents = {}
    
    pdf_loader = DirectoryLoader(".", glob=f"{data_path}/*.pdf", show_progress=True)
    documents['pdf_docs'] = pdf_loader.load()
    
    txt_loader = DirectoryLoader(".", glob=f"{data_path}/*.txt", show_progress=True)
    documents['txt_docs'] = txt_loader.load()
    
    csv_loader = CSVLoader(file_path=f"{data_path}/화장품데이터.csv", encoding='utf-8')
    documents['csv_docs'] = csv_loader.load()
    return documents
    
def print_documents(documents):
    print(f"문서의 수: {len(documents)})\n")
    for i in range(len(documents)):
        print(documents[i].metadata)
        
data_path = "SkinLution_data"
docs = load_documents(data_path)


# In[8]:


print_documents(docs['pdf_docs'])


# In[9]:


def split_documents(documents, chunk_size=500, chunk_overlap=100, add_start_index=True):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=add_start_index
    )
    return splitter.split_documents(documents)

pdf_splits = split_documents(docs['pdf_docs'], chunk_size=500, chunk_overlap=100)
print(f"PDF 문서 분할 후 총 청크 수: {len(pdf_splits)}")

txt_splits = split_documents(docs['txt_docs'], chunk_size=300, chunk_overlap=50)
print(f"TXT 문서 분할 후 총 청크 수: {len(txt_splits)}")


# In[10]:


def create_vectorstore(documents, embedding_model=None):
    embedding_model = embedding_model or OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents=documents, embedding=embedding_model)
    return vectorstore

def merge_vectorstores(primary_store, secondary_store):
    primary_store.merge_from(secondary_store)

pdf_vectorstore = create_vectorstore(pdf_splits)
txt_vectorstore = create_vectorstore(txt_splits)
cosmetic_vectorstore = create_vectorstore(docs['csv_docs'])

# PDF와 TXT 벡터 스토어 병합
merge_vectorstores(pdf_vectorstore, txt_vectorstore)


# In[15]:


# k is the number of chunks to retrieve
retriever1 = pdf_vectorstore.as_retriever(k=3)
retriever2 = cosmetic_vectorstore.as_retriever(k=50)


# In[16]:


# 선택된 벡터스토어에 따라 검색 수행하는 함수
def is_cosmetic_query(user_message):
    # 간단한 키워드 기반 분류기 => 머신러닝 모델로 바꿀 수 있음(사용자의 질문이 화장품 추천을 바라는 것인지 아닌지로 레이블링)
    cosmetic_keywords = ["화장품", "제품", "스킨케어", "로션", "크림"]
    return any(keyword in user_message for keyword in cosmetic_keywords)
                         
# 적절한 vectorstore를 선택하는 로직
def select_vectorstore(user_message):
    if is_cosmetic_query(user_message):
        return retriever2
    else:
        return retriever1
    


# In[17]:


# GPT LLM 생성
llm = ChatOpenAI(
    temperature=0,  # 창의성 (0.0 ~ 2.0) 낮을수록 같은 질문에 같은 대답
    model_name="gpt-4o-mini",  # 모델명
    #streaming=True,
    #callbacks=[StreamingStdOutCallbackHandler()], #스트리밍으로 답변 받기
)


# In[18]:


def perform_retrieval(user_message):
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
    return conversational_retrieval_chain


# In[19]:


import re

def main():
    demo_ephemeral_chat_history = ChatMessageHistory()
    printed_messages = []
    
    while True:
        user_message = input("질문할 내용을 입력하세요: ")
        if user_message == "-1":
            break
        
        demo_ephemeral_chat_history.add_user_message(user_message)
        
        # Perform retrieval based on user input
        response = perform_retrieval(user_message).invoke({"messages": demo_ephemeral_chat_history.messages})
        
        # Add AI response to the chat history
        demo_ephemeral_chat_history.add_ai_message(response["answer"])
        
        # Extract the title and metadata from the first document in the context
        first_document_title, first_document_metadata = extract_document_info(response)
        
        # Display new AI messages
        display_ai_messages(demo_ephemeral_chat_history, printed_messages)
        
        # Display document metadata if applicable
        if first_document_metadata:
            display_document_metadata(first_document_metadata)
        
        print("==========================================================")

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
    for key, value in metadata.items():
        if key == "source":
            match = re.search(r'\\(.+?)\s-\s', value)
            if match:
                value = match.group(1)
            print("답변에 활용한 정보:", value)

# 프로그램 시작
if __name__ == "__main__":
    main()


# In[78]:


from sentence_transformers import SentenceTransformer, util
from PIL import Image
import torch

# CLIP 모델 불러오기
clip_model = SentenceTransformer('clip-ViT-B-32')

# 피부 상태 설명 리스트 (필요에 따라 확장 가능)
skin_descriptions = [
    "얼굴이 붉은 피부",
    "건조한 피부",
    "유분기가 있는 피부",
    "평범한 피부",
]

# 각 피부 설명에 대한 텍스트 임베딩 생성
skin_description_embeddings = [clip_model.encode(desc, convert_to_tensor=True) for desc in skin_descriptions]

def analyze_skin_image(image_path):
    # 이미지 열기 및 CLIP 임베딩 생성
    image = Image.open(image_path).convert("RGB")
    image_embedding = clip_model.encode(image, convert_to_tensor=True)
    
    # 유사도 계산
    similarities = [util.pytorch_cos_sim(image_embedding, desc_embedding).item()
                    for desc_embedding in skin_description_embeddings]
    
    # 가장 높은 유사도 점수를 가진 피부 상태 설명 선택
    max_similarity_index = similarities.index(max(similarities))
    best_matching_description = skin_descriptions[max_similarity_index]
    best_similarity_score = similarities[max_similarity_index]
    
    return best_matching_description, best_similarity_score


# In[79]:


image_path = "평범피부.jpg"  # 사용자가 업로드한 이미지 파일 경로
description, score = analyze_skin_image(image_path)

print(f"해당 피부 상태로 가장 유사한 설명: {description}")
print(f"유사도 점수: {score:.2f}")

image_path = "피부1.jpg"  # 사용자가 업로드한 이미지 파일 경로
description, score = analyze_skin_image(image_path)

print(f"해당 피부 상태로 가장 유사한 설명: {description}")
print(f"유사도 점수: {score:.2f}")

image_path = "피부2.jpg"  # 사용자가 업로드한 이미지 파일 경로
description, score = analyze_skin_image(image_path)

print(f"해당 피부 상태로 가장 유사한 설명: {description}")
print(f"유사도 점수: {score:.2f}")

image_path = "민감피부2.jpg"  # 사용자가 업로드한 이미지 파일 경로
description, score = analyze_skin_image(image_path)

print(f"해당 피부 상태로 가장 유사한 설명: {description}")
print(f"유사도 점수: {score:.2f}")

image_path = "내피부.jpg"  # 사용자가 업로드한 이미지 파일 경로
description, score = analyze_skin_image(image_path)

print(f"해당 피부 상태로 가장 유사한 설명: {description}")
print(f"유사도 점수: {score:.2f}")

