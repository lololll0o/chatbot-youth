import streamlit as st
from llm import stream_ai_msg
import uuid

st.set_page_config(
    page_title="서울시 청년정책 관련 상담 챗봇",
    page_icon="🌱",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/projectnoonnu/2505-1@1.0/SeoulAlrimTTF-ExtraBold.woff2') format('woff2');
    
@font-face {
    font-family: 'SeoulNotice';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2505-1@1.0/SeoulAlrimTTF-ExtraBold.woff2') format('woff2');
    font-weight: 800;
    font-display: swap;
}
    
    .stApp {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
    }
    
    .main {
        background: transparent;
    }
        header[data-testid="stHeader"] {
        background: linear-gradient(180deg, #357ABD 0%, #4A90E2 100%) !important;
        border-bottom: 3px solid rgba(255, 255, 255, 0.3) !important;
    }

    .stApp > header,
    .stApp > div,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"] {
        background: transparent !important;
    }        
            
    [data-testid="stChatMessageContainer"] {
        background: transparent !important;
    }
    
    .block-container {
        padding-bottom: 2rem !important;
    }
            
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }
    
    footer {
        background: linear-gradient(0deg, #357ABD 0%, #4A90E2 100%) !important;
        border-top: 3px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    h1 {
        font-family: 'SeoulNotice', sans-serif !important;
        font-weight: 800 !important;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        text-align: center;
        padding: 20px 0;
        margin-bottom: 30px;
    }
    
    .stChatMessage {
        background: white !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
        font-family: 'SeoulNotice', sans-serif !important;
        font-weight: 500 !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: #E3F2FD !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        max-width: 70% !important;
        float: right !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: white !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        max-width: 70% !important;
        float: left !important;
    }
    
    .stChatMessage p {
        color: #333333 !important;
        text-shadow: 1px 1px 2px rgba(128, 128, 128, 0.2);
        font-family: 'SeoulHangang', sans-serif !important;
        font-weight: 500 !important;
        line-height: 1.6;
    }
    
    .stChatInputContainer {
        background: white !important;
        border: 2px solid #4A90E2 !important;
        border-radius: 25px !important;
        padding: 10px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stChatInput textarea {
        font-family: 'SeoulHangang', sans-serif !important;
        font-weight: 500 !important;
        color: #333333 !important;
    }
            
    .stChatInput textarea:focus {
        border : 2px solid #4A90E2 !important;
        outline : none !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        font-family: 'SeoulHangang', sans-serif !important;
        font-weight: 600 !important;
        padding: 10px 25px !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #357ABD 0%, #2E5F8A 100%) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
        font-family: 'SeoulHangang', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)


st.title("서울시 청년정책, 제가 요약해Dream ⛅")

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

for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])

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
