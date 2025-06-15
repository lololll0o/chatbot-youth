import streamlit as st
from llm import stream_ai_msg
import uuid

st.set_page_config(page_title="서울시 청년정책 관련 상담 챗봇", page_icon="🌱")
st.title("🚩서울 청년정책 관련 챗봇상담🌞")

query_params = st.query_params

if "session_id" in query_params:
    session_id = query_params["session_id"]
else :
    session_id = str(uuid.uuid4())
    st.query_params.update({"session_id": session_id})

if "session_id" not in st.session_state:
    st.session_state["session_id"] = session_id

if "message_list" not in st.session_state:
    st.session_state.message_list = []

# print("after) st.session_state >> ", st.session_state)

#이전 내용 출력
for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])

#채팅 메시지
placeholder = "청년정책 관련해 궁금한 점이 있으신가요?"
if user_question := st.chat_input(placeholder=placeholder):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    with st.spinner("열심히 생각중이에요 ! 잠시만 기다려주세요✈"):
        session_id = "user-session"
        ai_msg = stream_ai_msg(user_question, session_id=session_id)

        with st.chat_message("ai"):
            ai_msg = st.write_stream(ai_msg)
        st.session_state.message_list.append({"role":"ai", "content": ai_msg})

