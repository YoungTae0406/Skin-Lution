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
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain

def init_model():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    langchain_api_key = os.environ.get("LANGCHAIN_API_KEY")

    llm = ChatOpenAI(
        temperature=0,  # 창의성 (0.0 ~ 2.0) 낮을수록 같은 질문에 같은 대답
        max_tokens=3000,  # 최대 토큰수
        model_name="gpt-3.5-turbo",  # 모델명
        #streaming=True,
        #callbacks=[StreamingStdOutCallbackHandler()], #스트리밍으로 답변 받기
    )

    loader = DirectoryLoader("/data", glob="*.pdf")
    pdf_docs = loader.load()

    '''
    for i in range(len(pdf_docs)):
        print(pdf_docs[i].metadata)
    '''
    loader = DirectoryLoader("/data", glob="*.txt")
    txt_docs = loader.load()
    '''
    for i in range(len(txt_docs)):
        print(txt_docs[i].metadata)
    '''
    loader = CSVLoader(file_path='/data/cosmetics/화장품데이터.csv', encoding='utf-8')
    csv_docs = loader.load()

    pdf_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, #길이 500
        chunk_overlap=100, #겹치는 내용 100
        add_start_index=True #add_start_index=True초기 Document 내에서 각 분할 Document가 시작되는 문자 인덱스가 메타데이터 속성 "start_index"로 유지되도록 설정
    )
    pdf_splits = pdf_splitter.split_documents(pdf_docs)

    txt_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, 
        chunk_overlap=50, 
        add_start_index=True #add_start_index=True초기 Document 내에서 각 분할 Document가 시작되는 문자 인덱스가 메타데이터 속성 "start_index"로 유지되도록 설정
    )
    txt_splits = txt_splitter.split_documents(txt_docs)

    vectorstore1 = FAISS.from_documents(documents=pdf_splits, embedding=OpenAIEmbeddings())
    vectorstore2 = FAISS.from_documents(documents=txt_splits, embedding=OpenAIEmbeddings())
    cosmetic_vectorstore = FAISS.from_documents(documents=csv_docs, embedding=OpenAIEmbeddings())
    vectorstore1.merge_from(vectorstore2)

    retriever1 = vectorstore1.as_retriever(k=3)
    retriever2 = cosmetic_vectorstore.as_retriever(k=50)

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

# model init 하기
init_model()

class ChatGPTModel:
    def __init__(self):
        self.chat_history = ChatMessageHistory()
        self.printed_messages = []

    def get_response(self, user_message):
        self.chat_history.add_user_message(user_message)
        retrieval_chain = perform_retrieval(user_message)
        response = retrieval_chain.invoke({"messages": self.chat_history.messages})
        
        self.chat_history.add_ai_message(response["answer"])

        first_document_title = None
        if "context" in response and response["context"]:
            first_document = response["context"][0]
            first_document_title = first_document.page_content.split('\n')[0].strip()

        ai_messages = [msg.content for msg in self.chat_history.messages if isinstance(msg, AIMessage)]
        new_messages = []
        for msg in ai_messages:
            if msg not in self.printed_messages:
                new_messages.append(msg)
                self.printed_messages.append(msg)
        
        return {
            "response": new_messages,
            "document_title": first_document_title
        }

# ChatGPTModel 인스턴스를 생성합니다.
chat_gpt_model = ChatGPTModel()
