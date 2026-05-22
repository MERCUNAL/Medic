import streamlit as st
import uuid

from backend import get_response


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Medical Chatbot",
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
    background-color: #f6fff8;
}


/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #0f5132;
    border-right: 2px solid #198754;
}


section[data-testid="stSidebar"] * {
    color: white !important;
}


/* CHAT INPUT */
.stChatInputContainer {
    background-color: black;
    border-top: 2px solid #198754;
}


/* USER CHAT */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background-color: #d1f7dc;
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 10px;
}


/* ASSISTANT CHAT */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background-color: white;
    border: 1px solid #c7f0d2;
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 10px;
}


/* BUTTONS */
.stButton > button {
    background-color: #198754;
    color: white;
    border-radius: 10px;
    border: none;
    transition: 0.3s;
}


.stButton > button:hover {
    background-color: #157347;
    color: white;
}

/* TITLE */
h1 {
    color: black !important;
}


/* CHAT MESSAGES */
[data-testid="stChatMessage"] {
    color: black !important;
}


/* CHAT MESSAGE TEXT */
[data-testid="stMarkdownContainer"] p {
    color: black !important;
}

/* CHAT TITLE */
h1 {
    color: #198754;
    font-weight: 700;
}
/* RETRIEVED DOCUMENTS / DATABASE TEXT */
/* ASSISTANT MESSAGE TEXT */
[data-testid="stChatMessage"] * {
    color: black !important;
}


/* FORCE MARKDOWN TEXT TO BLACK */
.stMarkdown,
.stMarkdown p,
.stMarkdown span,
.stMarkdown div,
.stMarkdown li,
.stMarkdown strong {
    color: black !important;
}
/* SCROLLBAR */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #198754;
    border-radius: 10px;
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
        "messages": []
    }


# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.title("💬 Chats")


    # NEW CHAT BUTTON
    if st.button("➕ New Chat", use_container_width=True):

        new_chat_id = str(uuid.uuid4())

        st.session_state.all_chats[new_chat_id] = {
            "title": "New Chat",
            "messages": []
        }

        st.session_state.current_chat = new_chat_id

        st.rerun()


    st.divider()


    # CHAT LIST
    for chat_id, chat_data in st.session_state.all_chats.items():

        chat_title = chat_data["title"]

        if st.button(
            chat_title,
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
# MAIN UI
# =========================
st.title("🩺 Medical Chatbot")
st.markdown("Hello, how can we help you today?")

# =========================
# DISPLAY MESSAGES
# =========================
for msg in current_chat["messages"]:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =========================
# CHAT INPUT
# =========================
user_input = st.chat_input("Ask a medical question...")


if user_input:

    # UPDATE TITLE FROM FIRST MESSAGE
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


    # GET AI RESPONSE
    with st.spinner("Thinking..."):

        ai_response = get_response(
            user_input=user_input,
            thread_id=current_chat_id
        )


    # STORE AI MESSAGE
    current_chat["messages"].append({
        "role": "assistant",
        "content": ai_response
    })


    # DISPLAY AI RESPONSE
    with st.chat_message("assistant"):
        st.markdown(ai_response)

