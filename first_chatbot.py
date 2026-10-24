
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
from openai import OpenAI, AuthenticationError


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Your Custom ChatGPT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# 2. SESSION STATE INITIALIZATION
# --------------------------------------------------

if "api_key" not in st.session_state:
    st.session_state.api_key = None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

if "system_role" not in st.session_state:
    st.session_state.system_role = "You are a helpful assistant."


# --------------------------------------------------
# 3. API KEY LOGIN SCREEN
# --------------------------------------------------

if not st.session_state.authenticated:

    # Hide sidebar before login
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }

        .block-container {
            max-width: 500px;
            padding-top: 12vh;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<h1 style='text-align:center;'>🤖 Salman's ChatGPT</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;'>Enter your OpenAI API key to continue</p>",
        unsafe_allow_html=True
    )

    with st.form("login_form"):

        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-..."
        )

        login_button = st.form_submit_button(
            "Connect & Continue",
            use_container_width=True,
            type="primary"
        )

    if login_button:

        api_key = api_key.strip()

        if not api_key:
            st.error("Please enter your OpenAI API key.")

        else:

            with st.spinner("Validating API key..."):

                try:

                    # Check key with OpenAI
                    client = OpenAI(api_key=api_key)
                    client.models.list()

                    st.session_state.api_key = api_key
                    st.session_state.authenticated = True

                    st.rerun()

                except AuthenticationError:
                    st.error("Invalid API key. Please check your key.")

                except Exception:
                    st.error(
                        "Could not validate the API key. "
                        "Please check your network and API access."
                    )

    st.stop()


# --------------------------------------------------
# 4. CREATE A NEW CHAT
# --------------------------------------------------

def create_new_chat():

    st.session_state.chat_counter += 1

    chat_id = str(st.session_state.chat_counter)

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": []
    }

    st.session_state.current_chat = chat_id


# --------------------------------------------------
# 5. SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("🤖 Custom ChatGPT")

    st.divider()

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):
        create_new_chat()
        st.rerun()

    st.subheader("Chat History")

    # Show newest chats first
    for chat_id in reversed(
        list(st.session_state.chats.keys())
    ):

        chat_title = st.session_state.chats[chat_id]["title"]

        if st.button(
            f"💬 {chat_title}",
            key=f"chat_{chat_id}",
            use_container_width=True
        ):

            st.session_state.current_chat = chat_id
            st.rerun()

    st.divider()

    st.subheader("Settings")

    st.text_area(
        "System Role",
        key="system_role",
        height=100
    )

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.api_key = None
        st.session_state.authenticated = False
        st.session_state.chats = {}
        st.session_state.current_chat = None
        st.session_state.chat_counter = 0

        st.rerun()


# --------------------------------------------------
# 6. INITIALIZE CHAT IF NONE EXISTS
# --------------------------------------------------

if st.session_state.current_chat is None:
    create_new_chat()


# --------------------------------------------------
# 7. MAIN CHAT SCREEN
# --------------------------------------------------

st.title("Salman's ChatGPT")

current_chat_id = st.session_state.current_chat

messages = st.session_state.chats[
    current_chat_id
]["messages"]


# --------------------------------------------------
# 8. DISPLAY CHAT HISTORY IN MAIN SCREEN
# --------------------------------------------------

for message in messages:

    if isinstance(message, HumanMessage):

        with st.chat_message("user"):
            st.markdown(message.content)

    elif isinstance(message, AIMessage):

        with st.chat_message("assistant"):
            st.markdown(message.content)


# --------------------------------------------------
# 9. CENTER WELCOME MESSAGE
# --------------------------------------------------

if len(messages) == 0:

    st.markdown(
        """
        <div style="
            text-align: center;
            padding-top: 12vh;
            padding-bottom: 8vh;
        ">
            <h1>✨ How can I help you today?</h1>
            <p>Ask me anything to get started.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# 10. MAIN CHAT INPUT
# --------------------------------------------------

user_prompt = st.chat_input(
    "Message your assistant..."
)


# --------------------------------------------------
# 11. PROCESS USER MESSAGE
# --------------------------------------------------

if user_prompt:

    # Store user message
    messages.append(
        HumanMessage(content=user_prompt)
    )

    # Update chat title using first message
    if len(messages) == 1:

        st.session_state.chats[
            current_chat_id
        ]["title"] = user_prompt[:30]

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Prepare messages for OpenAI
    api_messages = [
        SystemMessage(
            content=st.session_state.system_role
            or "You are a helpful assistant."
        )
    ] + messages

    # Initialize OpenAI model
    chat = ChatOpenAI(
        model="gpt-5.2",
        api_key=st.session_state.api_key
    )

    # Generate assistant response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = chat.invoke(api_messages)

                st.markdown(response.content)

                # Save assistant response
                messages.append(
                    AIMessage(content=response.content)
                )

            except Exception:
                st.error(
                    "Unable to generate a response. "
                    "Please check your API key, "
                    "model access, and billing."
                )
