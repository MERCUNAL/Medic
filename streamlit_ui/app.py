import streamlit as st
import uuid
import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(PROJECT_ROOT)

from rag.chatbot import get_response


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Medic",
    page_icon="🩺",
    layout="wide"
)
# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>

/* MAIN APP */
.stApp {
    background-color: #f4fff7;
}


/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f5132 0%, #198754 100%);
    border-right: 1px solid #198754;
}


/* SIDEBAR TEXT */
section[data-testid="stSidebar"] * {
    color: red !important;
}


/* TITLE */
.main-title {
    font-size: 42px;
    font-weight: 700;
    color: #198754;
    margin-bottom: 0px;
}


.sub-title {
    color: #4f4f4f;
    margin-top: -10px;
    margin-bottom: 20px;
}


/* USER CHAT */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background: #d1f7dc;
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 14px;
    border: 1px solid #b7ebc4;
}


/* ASSISTANT CHAT */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background: white;
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 14px;
    border: 1px solid #d8f3dc;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.03);
}


/* MESSAGE TEXT */
[data-testid="stChatMessage"] * {
    color: black !important;
}


/* BUTTONS */
.stButton > button {
    width: 100%;
    background-color: white;
    color: #198754;
    border-radius: 12px;
    border: 1px solid #198754;
    padding: 10px 14px;
    transition: all 0.2s ease;
    font-weight: 500;
}


.stButton > button:hover {
    background-color: #198754;
    color: white;
    transform: scale(1.02);
}


/* CHAT INPUT */
.stChatInputContainer {
    background-color: white;
    border-top: 1px solid #d8f3dc;
}


/* SCROLLBAR */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #198754;
    border-radius: 10px;
}


/* SUGGESTION TITLE */
.suggestion-title {
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 8px;
    color: #198754;
}

</style>
""", unsafe_allow_html=True)


# =========================
# SESSION STATE
# =========================
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_chat" not in st.session_state:

    new_chat_id = str(uuid.uuid4())

    st.session_state.current_chat = new_chat_id

    st.session_state.all_chats[new_chat_id] = {
        "title": "New Chat",
        "messages": [],
        "suggestions": []
    }


if "selected_option" not in st.session_state:
    st.session_state.selected_option = None


# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.title("💬 Chats")

    # NEW CHAT
    if st.button("➕ New Chat", use_container_width=True):

        new_chat_id = str(uuid.uuid4())

        st.session_state.all_chats[new_chat_id] = {
            "title": "New Chat",
            "messages": [],
            "suggestions": []
        }

        st.session_state.current_chat = new_chat_id

        st.rerun()

    st.divider()

    # CHAT LIST
    for chat_id, chat_data in st.session_state.all_chats.items():

        if st.button(
            chat_data["title"],
            key=chat_id,
            use_container_width=True
        ):

            st.session_state.current_chat = chat_id
            st.rerun()


# =========================
# CURRENT CHAT
# =========================
current_chat_id = st.session_state.current_chat
current_chat = st.session_state.all_chats[current_chat_id]


# =========================
# MAIN HEADER
# =========================
st.markdown(
    '<div class="main-title">🩺 Medic</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Your AI medical support assistant</div>',
    unsafe_allow_html=True
)


# =========================
# DISPLAY CHAT HISTORY
# =========================
for msg in current_chat["messages"]:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =========================
# CHAT INPUT
# =========================
typed_input = st.chat_input("Ask a medical question...")


# =========================
# PRIORITY:
# BUTTON CLICK > TEXT INPUT
# =========================
user_input = None

if st.session_state.selected_option:

    user_input = st.session_state.selected_option
    st.session_state.selected_option = None

elif typed_input:

    user_input = typed_input


# =========================
# PROCESS MESSAGE
# =========================
if user_input:

    # UPDATE TITLE
    if current_chat["title"] == "New Chat":
        current_chat["title"] = user_input[:30]

    # STORE USER MESSAGE
    current_chat["messages"].append({
        "role": "user",
        "content": user_input
    })

    # DISPLAY USER MESSAGE
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI RESPONSE
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer, options = get_response(
                user_input=user_input,
                thread_id=current_chat_id
            )

            st.markdown(answer)

    # STORE ASSISTANT RESPONSE
    current_chat["messages"].append({
        "role": "assistant",
        "content": answer
    })

    # STORE SUGGESTIONS
    current_chat["suggestions"] = options

    st.rerun()


# =========================
# SUGGESTED OPTIONS
# =========================
if current_chat.get("suggestions"):

    st.markdown(
        """
        <div class="suggestion-title">
            Suggested Questions
        </div>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns(len(current_chat["suggestions"]))

    for i, option in enumerate(current_chat["suggestions"]):

        with cols[i]:

            if st.button(
                option,
                key=f"option_{i}",
                use_container_width=True
            ):

                st.session_state.selected_option = option
                st.rerun()