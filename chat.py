import streamlit as st
from llm import stream_ai_msg
import uuid

# 페이지 설정
st.set_page_config(
    page_title="서울시 청년정책 관련 상담 챗봇",
    page_icon="🌱",
    layout="wide",
)

# 타이틀 출력
st.title("서울시 청년정책, 제가 요약해드림 🧠")

# 세션 ID 처리
query_params = st.query_params
if "session_id" in query_params:
    session_id = query_params["session_id"]
else:
    session_id = str(uuid.uuid4())
    st.query_params.update({"session_id": session_id})

if "session_id" not in st.session_state:
    st.session_state["session_id"] = session_id

if "message_list" not in st.session_state:
    st.session_state.message_list = []

# 이전 대화 출력
for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 채팅 입력 처리
placeholder = "청년정책 관련해 궁금한 점이 있으신가요?"
if user_question := st.chat_input(placeholder=placeholder):
    with st.chat_message("user"):
        st.write(user_question)

    st.session_state.message_list.append({"role": "user", "content": user_question})

    with st.spinner("열심히 생각중이에요 ! 잠시만 기다려주세요💬"):
        session_id = st.session_state["session_id"]
        ai_stream = stream_ai_msg(user_question, session_id=session_id)

        full_answer = ""
        with st.chat_message("ai"):
            for chunk in st.write_stream(ai_stream):
                full_answer += chunk

        st.session_state.message_list.append({"role": "ai", "content": full_answer})
