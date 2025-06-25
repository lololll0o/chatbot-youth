import streamlit as st
from llm import stream_ai_msg
import uuid

st.set_page_config(page_title="서울시 청년정책 관련 상담 챗봇", page_icon="🌱", layout="wide",)
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css">
            
<style>
html, body, .stApp {
    font-family: 'Pretendard', sans-serif !important;
    background: linear-gradient(135deg, #b2dbff 0%, #fefcea 100%);
    margin: 0px;
    padding: 30px;
    margin-bottom: 0px;
}

.title-shadow {
    text-align: center;
    font-size: 2.5rem;
    padding: 30px 40px;
    margin-bottom: 30px;

    background: rgba(255, 255, 255, 0.15);
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.5);
    border-radius: 32px; 
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15); 

    font-weight: 700;
}

[data-testid="stChatMessageContent"] {
    background: rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 2px solid rgba(255, 255, 255, 0.5);
    border-radius: 24px;  
    padding: 16px 20px;
    margin: 10px 0;
    color: #1f1f1f;
    box-shadow: 0 6px 20px rgba(0,0,0,0.06); 
}

div:has(.stMarkdown) + div [data-testid="stChatMessageContent"] {
    background: rgba(255, 255, 255, 0.8); 
    border: 2px solid rgba(255, 255, 255, 1); 
    color: #111111;
    border-radius: 24px;  
}

[data-testid="stChatMessageContent"] pre {
    background: transparent !important;
}

.chat-user-text {
    padding: 12px 20px;
    background: rgba(255, 255, 255, 0.8);
    border: 2px solid #ffffff;
    border-radius: 20px;   
    color: #111111;
    font-size: 1rem;
    font-weight: 500;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}

</style>

<h1 class="title-shadow"> <span>서울시 청년정책, 제가 요약해드림 🧠</span> </h1>
<div style="margin-bottom: 40px;"></div>
""", unsafe_allow_html=True)



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

    with st.spinner("열심히 생각중이에요 ! 잠시만 기다려주세요💬"):
        session_id = "user-session"
        ai_msg = stream_ai_msg(user_question, session_id=session_id)

        with st.chat_message("ai"):
            ai_msg = st.write_stream(ai_msg)
        st.session_state.message_list.append({"role":"ai", "content": ai_msg})
