import streamlit as st
from llm import stream_ai_msg
import uuid

# 페이지 설정
st.set_page_config(
    page_title="서울시 청년정책 관련 상담 챗봇",
    page_icon="🌱",
    layout="wide",
)

# 전역 스타일 삽입 (폰트, 배경, 채팅 말풍선 등 포함)
st.markdown("""
<style>
@font-face {
    font-family: 'Pretendard';
    font-style: normal;
    font-weight: 400;
    src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/woff2/Pretendard-Regular.woff2') format('woff2');
}

.stApp {
    font-family: 'Pretendard', sans-serif !important;
    background: linear-gradient(135deg, #b2dbff 0%, #fefcea 100%) !important;
}

main, .block-container {
  background: transparent !important;
}
            
h1.title-shadow {
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

[data-testid="stChatInput"] {
  background: transparent !important;
  border-top: none !important;
}

[data-testid="stChatInput"] textarea {
  background: rgba(255,255,255,0.8);
  border: 2px solid #ffffff;
  border-radius: 16px;
  color: #111111;
  font-size: 1rem;
  font-weight: 500;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}

[data-testid="stChatMessageContent"] {
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 24px;
  padding: 16px 20px;
  margin: 12px 0px;
  color: #1f1f1f;
  box-shadow: 0 6px 20px rgba(0,0,0,0.06);
}


</style>
""", unsafe_allow_html=True)

# 타이틀 출력
st.markdown("""
<h1 class="title-shadow">서울시 청년정책, 제가 요약해드림 🧠</h1>
""", unsafe_allow_html=True)

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
