import os

from dotenv import load_dotenv
from pinecone import Pinecone

from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import (ChatPromptTemplate, FewShotPromptTemplate,
                                    MessagesPlaceholder, PromptTemplate)
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from config import ex


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
너는 다중턴 대화 기반 Q&A 시스템의 전문 질문 정제 엔진이야. 사용자가 입력한 현재 질문(current_query)과 직전의 대화 흐름(chat_history)을 바탕으로, 검색 최적화에 적합한 하나의 독립형 질문으로 고쳐야 해.

너의 역할은 다음과 같아:

- "chat_history"를 읽고, 사용자 의도가 현재 질문에서 생략된 부분(주어, 목적어, 명사, 시간, 장소 등)이 있다면 이를 자연스럽게 보완해.

- 이전 질문이나 답변에서 언급된 주요 개념, 고유명사, 인물, 시간 정보 등을 반영하여 맥락이 끊기지 않도록 한다.

- 정보가 불충분하거나 모호한 경우, 가능한 추론을 적용하되 사실을 왜곡하지 말고 "적절히 일반화된 형태"로 완성한다.

- 질문을 수정할 때는 문법적으로 완전한 하나의 문장으로 고쳐야 하며, 끝에는 물음표(?)를 붙인다.

- 이미 명확한 질문이라면 변형하지 말고 그대로 반환한다.

- 절대로 질문에 대해 답변하지 마라. 오직 질문을 재구성하는 역할만 수행해라.
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
def build_few_shot() -> str:
    example_prompt = PromptTemplate.from_template("질문: {input}\n\n답변: {answer}")

    few_shot_prompt = FewShotPromptTemplate(
        examples=ex,
        example_prompt=example_prompt,
        prefix="다음 질문에 답변하시오.",
        suffix="질문 : {input}",
        input_variables=["input"],
    )

    formmated_few_shot_prompt = few_shot_prompt.format(input="{input}")

    return formmated_few_shot_prompt

def build_qa_prompt():
    system_prompt = (
        """[identity]
        -너는 서울시에서 시행중인 청년관련 정책 담당자야.
        - [context]를 참고하여 사용자의 질문에 답변해.
        - 말투는 최대한 사용자의 질문 눈높이에 맞춰서 답변해줘.
        -정책과 관련된 질문을 물어본다면 답변 마지막엔 너가 어디서 이 답변을 참고한건지 [ex) 참고한 문서 - 정책번호 : "", 정책명 :"", 정책 유형 :""  ]후미에 간략하게라도 꼭 달아줘.
        - 문서에 적혀있는 내용과 비슷한 질문에는 최선을 다해 질문하려 노력해.
        - 하지만 그 외의 질문에는 "답변할 수 없습니다"라고 출력해.

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

