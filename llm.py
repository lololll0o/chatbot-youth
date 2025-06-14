import os

from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

def load_llm(model='gpt-4o-mini'):
    return ChatOpenAI(model=model)

def load_vectorstore():
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

    embedding = OpenAIEmbeddings(model="text-embedding-3-large")
    Pinecone(api_key=PINECONE_API_KEY)
    index_name = "docx-list"

    database = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embedding,
    )

    return database

#
    
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def build_history_aware_retriever(llm, retriever):
    contextualize_q_system_prompt = (
         '''
- 너는 대화형 Q&A 시스템의 고도화된 질문 전처리 담당이야.
- 사용자의 질문과 제공된 (chat history)을 참고해서 검색에 가장 적합한 문장으로 사용자의 질문을 명확하게 수정해.
- 'chat history'를 참고해서 현재 질문에 생략된 주어, 목적어 등 맥락상 필요한 정보를 보충하여 질문을 완성해.
- 특히 이전대화에서 언급된 키워드나 명사가 있다면 현재 질문에 자연스럽게 통합시켜.
- 만약 질문이 이미 명확하면 그대로 반환해.
- 질문에 대해 절대 답변하지 말고, 단지 "이해 가능한 독립 질문"으로 고치기만 해.
'''
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    return history_aware_retriever

## few_shot





def build_qa_prompt():
    system_prompt = (
        """[identity]
        -너는 서울시에서 시행중인 청년관련 정책을 전부 기억하고있는 전문가야.
        - [context]를 참고하여 사용자의 질문에 답변해.
        - 답변 마지막엔 너가 어디서 이 답변을 참고한건지 [ex) 참고한 정책번호 : "", 정책명 :"", 정책 유형 :""  ]후미에 꼭 달아줘.
        - 문서에 적혀있는 내용 이외의 질문에는 "답변할 수 없습니다"라고 출력해.

        [context]
        {context}        
        """
    )

    qa_prompt= ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    return qa_prompt



def build_conversational_chain():
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

    database = load_vectorstore()
    llm = load_llm()
    retriever = database.as_retriever(search_kwargs={"k":3})

    history_aware_retriever = build_history_aware_retriever(llm, retriever)

    qa_prompt = build_qa_prompt()
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ).pick("answer")

    return conversational_rag_chain

## AI MESSAGE 
def stream_ai_msg(user_message, session_id="default"):
    rag_chain = build_conversational_chain()

    ai_message = rag_chain.stream(
        {"input": user_message},
        config={"configurable": {"session_id" : session_id}},
    )

    print(f"대화 내역 >>{get_session_history(session_id)}\n\n")
    print("*" * 50 + "\n")
    print(f'[stream_ai_msg 함수 내 출력] session_id >> {session_id}')

    return ai_message

