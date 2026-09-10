import html
import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from supabase import Client, create_client

from config import APP_URL, SUPABASE_ANON_KEY, SUPABASE_URL
from services.chat_service import get_thread_messages, send_chat_message


st.set_page_config(
    page_title="MemoryChat",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --memory-purple: #7c3aed;
        --memory-purple-dark: #5b21b6;
        --memory-sidebar: #171126;
        --memory-sidebar-soft: #241c38;
        --memory-surface: #f7f8fc;
        --memory-card: #ffffff;
        --memory-text: #1f2937;
        --memory-muted: #8b8a98;
        --memory-border: #dde1eb;
    }

    html, body, [class*="css"] {
        font-family: "Inter", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 90% 5%, rgba(124, 58, 237, 0.06), transparent 30%),
            var(--memory-surface);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #151023 0%, #1d1731 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2.2rem;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff;
    }

    [data-testid="stSidebar"] a {
        color: #a99dbf !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.09);
    }

    .memory-brand {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin: 0.15rem 0 0.15rem;
    }

    .memory-logo {
        display: grid;
        width: 40px;
        height: 40px;
        place-items: center;
        border-radius: 12px;
        color: white;
        font-size: 1.25rem;
        background: linear-gradient(135deg, #8b5cf6, #6d28d9);
        box-shadow: 0 10px 24px rgba(124, 58, 237, 0.32);
    }

    .memory-brand-name {
        color: white;
        font-size: 1.2rem;
        font-weight: 800;
        letter-spacing: -0.04em;
    }

    .memory-tagline {
        margin: 0 0 1.15rem;
        color: #a99dbf;
        font-size: 0.74rem;
    }

    .sidebar-heading {
        margin: 1.5rem 0 0.7rem;
        color: white;
        font-size: 0.95rem;
        font-weight: 700;
    }

    [data-testid="stSidebar"] .stButton > button {
        min-height: 42px;
        border-radius: 11px;
        border: 1px solid rgba(255, 255, 255, 0.13);
        background: rgba(255, 255, 255, 0.045);
        color: white;
        font-weight: 500;
        transition: all 0.18s ease;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: rgba(139, 92, 246, 0.9);
        background: rgba(124, 58, 237, 0.18);
        transform: translateY(-1px);
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        border: none;
        background: linear-gradient(135deg, #7c3aed, #6524c8);
        box-shadow: 0 8px 22px rgba(124, 58, 237, 0.22);
    }

    .main .block-container {
        max-width: 950px;
        padding-top: 4.2rem;
        padding-bottom: 7rem;
    }

    .eyebrow {
        margin-bottom: 0.65rem;
        color: var(--memory-purple);
        font-size: 0.69rem;
        font-weight: 800;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }

    .conversation-title {
        margin: 0;
        color: #20273a;
        font-size: clamp(2rem, 4vw, 2.55rem);
        font-weight: 800;
        letter-spacing: -0.055em;
        line-height: 1.1;
    }

    .memory-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        margin: 1rem 0 1.25rem;
        padding: 0.38rem 0.72rem;
        border: 1px solid #a7efc1;
        border-radius: 999px;
        background: #effdf4;
        color: #087a3f;
        font-size: 0.72rem;
        font-weight: 600;
    }

    [data-testid="stChatMessage"] {
        margin: 0 0 1.35rem;
        padding: 1rem 1.05rem;
        border: 1px solid var(--memory-border);
        border-radius: 16px;
        background: var(--memory-card);
        box-shadow: 0 10px 30px rgba(31, 41, 55, 0.055);
    }

    [data-testid="stChatMessage"] p {
        color: var(--memory-text);
        line-height: 1.65;
    }

    [data-testid="stChatInput"] {
        border-radius: 14px;
        box-shadow: 0 10px 30px rgba(31, 41, 55, 0.09);
    }

    .welcome-card {
        margin-top: 1.4rem;
        padding: 1.25rem 1.35rem;
        border: 1px solid #ddd7fb;
        border-radius: 16px;
        background: linear-gradient(135deg, #f4f1ff, #ffffff);
        color: #4c3b77;
        box-shadow: 0 12px 35px rgba(124, 58, 237, 0.06);
    }

    .auth-shell {
        max-width: 700px;
        margin: 1.2rem auto 0;
    }

    .auth-title {
        margin-bottom: 0.2rem;
        color: #20273a;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.055em;
    }

    .auth-subtitle {
        margin-bottom: 1.35rem;
        color: var(--memory-muted);
    }

    .stTextInput input {
        border-radius: 11px;
    }

    .stFormSubmitButton > button,
    .main .stButton > button {
        min-height: 42px;
        border-radius: 11px;
        font-weight: 600;
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 2rem;
        }

        .conversation-title,
        .auth-title {
            font-size: 2rem;
        }
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def initialize_session_state() -> None:
    defaults = {
        "access_token": None,
        "refresh_token": None,
        "user_id": None,
        "user_email": None,
        "active_conversation_id": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_session_state() -> None:
    for key in (
        "access_token",
        "refresh_token",
        "user_id",
        "user_email",
        "active_conversation_id",
    ):
        st.session_state[key] = None


def new_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def authenticated_supabase_client() -> Client:
    client = new_supabase_client()

    auth_response = client.auth.set_session(
        st.session_state.access_token,
        st.session_state.refresh_token,
    )

    if auth_response.session:
        st.session_state.access_token = auth_response.session.access_token
        st.session_state.refresh_token = auth_response.session.refresh_token

    return client


def save_login_session(auth_response) -> bool:
    if not auth_response.user or not auth_response.session:
        return False

    st.session_state.user_id = str(auth_response.user.id)
    st.session_state.user_email = auth_response.user.email
    st.session_state.access_token = auth_response.session.access_token
    st.session_state.refresh_token = auth_response.session.refresh_token
    st.session_state.active_conversation_id = None

    return True


def register_user(
    full_name: str,
    phone: str,
    email: str,
    password: str,
):
    client = new_supabase_client()

    return client.auth.sign_up(
        {
            "email": email,
            "password": password,
            "options": {
                "email_redirect_to": APP_URL,
                "data": {
                    "full_name": full_name,
                    "phone": phone or None,
                },
            },
        }
    )


def login_user(email: str, password: str):
    client = new_supabase_client()

    return client.auth.sign_in_with_password(
        {
            "email": email,
            "password": password,
        }
    )


def load_conversations(client: Client) -> list[dict]:
    response = (
        client.table("conversations")
        .select("id, user_id, title, created_at, updated_at")
        .eq("user_id", st.session_state.user_id)
        .order("updated_at", desc=True)
        .execute()
    )

    return response.data or []


def create_conversation(client: Client) -> dict:
    conversation = {
        "id": str(uuid.uuid4()),
        "user_id": st.session_state.user_id,
        "title": "New conversation",
    }

    response = (
        client.table("conversations")
        .insert(conversation)
        .execute()
    )

    return response.data[0]


def update_conversation_title(
    client: Client,
    conversation_id: str,
    title: str,
) -> None:
    (
        client.table("conversations")
        .update({"title": title})
        .eq("id", conversation_id)
        .eq("user_id", st.session_state.user_id)
        .execute()
    )


def make_conversation_title(message: str) -> str:
    clean_message = " ".join(message.strip().split())

    if len(clean_message) <= 48:
        return clean_message

    return f"{clean_message[:45].rstrip()}..."


def display_text(content) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, dict) and block.get("text"):
                text_parts.append(block["text"])

        if text_parts:
            return "\n".join(text_parts)

    return str(content)


def render_auth_page() -> None:
    st.markdown(
        """
        <div class="auth-shell">
            <div class="auth-title">MemoryChat</div>
            <div class="auth-subtitle">
                Persistent conversations with short-term and long-term memory
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )
            submitted = st.form_submit_button(
                "Login",
                use_container_width=True,
                type="primary",
            )

        if submitted:
            if not email.strip() or not password:
                st.error("Enter your email and password.")
            else:
                try:
                    response = login_user(
                        email=email.strip(),
                        password=password,
                    )

                    if save_login_session(response):
                        st.rerun()
                    else:
                        st.error("Login failed. Please verify your email first.")
                except Exception as error:
                    st.error(f"Login failed: {error}")

    with register_tab:
        with st.form("registration_form"):
            full_name = st.text_input(
                "Full name",
                key="register_name",
            )
            phone = st.text_input(
                "Phone number (optional)",
                key="register_phone",
            )
            email = st.text_input(
                "Registration email",
                key="register_email",
            )
            password = st.text_input(
                "Create password",
                type="password",
                key="register_password",
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="register_confirm_password",
            )
            submitted = st.form_submit_button(
                "Create account",
                use_container_width=True,
                type="primary",
            )

        if submitted:
            if not full_name.strip() or not email.strip() or not password:
                st.error("Full name, email, and password are required.")
            elif password != confirm_password:
                st.error("The passwords do not match.")
            elif len(password) < 6:
                st.error("Your password must contain at least 6 characters.")
            else:
                try:
                    response = register_user(
                        full_name=full_name.strip(),
                        phone=phone.strip(),
                        email=email.strip(),
                        password=password,
                    )

                    if response.user:
                        st.success(
                            f"Account created. A confirmation email was sent to "
                            f"{email.strip()}. Open that email, confirm your address, "
                            "and then return here to log in."
                        )
                    else:
                        st.error("Registration could not be completed.")
                except Exception as error:
                    st.error(f"Registration failed: {error}")


def render_sidebar(
    client: Client,
    conversations: list[dict],
) -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="memory-brand">
                <div class="memory-logo">✦</div>
                <div class="memory-brand-name">MemoryChat</div>
            </div>
            <div class="memory-tagline">Persistent AI conversations</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"[{st.session_state.user_email}]"
            f"(mailto:{st.session_state.user_email})"
        )

        if st.button(
            "+  New conversation",
            type="primary",
            use_container_width=True,
        ):
            try:
                conversation = create_conversation(client)
                st.session_state.active_conversation_id = conversation["id"]
                st.rerun()
            except Exception as error:
                st.error(f"Could not create the conversation: {error}")

        st.markdown(
            '<div class="sidebar-heading">Conversations</div>',
            unsafe_allow_html=True,
        )

        if not conversations:
            st.caption("No conversations yet.")

        for conversation in conversations:
            is_active = (
                conversation["id"]
                == st.session_state.active_conversation_id
            )

            if st.button(
                conversation["title"],
                key=f"conversation_{conversation['id']}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.active_conversation_id = conversation["id"]
                st.rerun()

        st.divider()

        if st.button(
            "Log out",
            use_container_width=True,
            key="logout_button",
        ):
            try:
                client.auth.sign_out()
            finally:
                clear_session_state()
                st.rerun()


def render_chat_page(
    client: Client,
    conversations: list[dict],
) -> None:
    conversation_by_id = {
        conversation["id"]: conversation
        for conversation in conversations
    }

    active_id = st.session_state.active_conversation_id

    if active_id not in conversation_by_id:
        active_id = None
        st.session_state.active_conversation_id = None

    if not active_id:
        st.markdown(
            '<div class="eyebrow">Memory-aware assistant</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h1 class="conversation-title">Welcome to MemoryChat</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="welcome-card">
                Create a new conversation or select an existing conversation
                from the sidebar to begin.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    active_conversation = conversation_by_id[active_id]

    st.markdown(
        '<div class="eyebrow">Active conversation</div>',
        unsafe_allow_html=True,
    )
    safe_title = html.escape(active_conversation["title"])

    st.markdown(
        f'<h1 class="conversation-title">{safe_title}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="memory-badge">
            ● Short-term + long-term memory active
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        messages = get_thread_messages(active_id)
    except Exception as error:
        st.error(f"Could not load this conversation: {error}")
        messages = []

    for message in messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user", avatar="👤"):
                st.markdown(display_text(message.content))
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant", avatar="✨"):
                st.markdown(display_text(message.content))

    prompt = st.chat_input("Message MemoryChat...")

    if not prompt:
        return

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant", avatar="✨"):
            with st.spinner("Thinking..."):
                assistant_message = send_chat_message(
                    thread_id=active_id,
                    user_id=st.session_state.user_id,
                    message=prompt,
                )

            st.markdown(display_text(assistant_message.content))

        title = active_conversation["title"]

        if title == "New conversation":
            title = make_conversation_title(prompt)

        update_conversation_title(
            client=client,
            conversation_id=active_id,
            title=title,
        )

        st.rerun()

    except Exception as error:
        st.error(f"MemoryChat could not answer: {error}")


initialize_session_state()

is_logged_in = all(
    (
        st.session_state.access_token,
        st.session_state.refresh_token,
        st.session_state.user_id,
    )
)

if not is_logged_in:
    render_auth_page()
    st.stop()

try:
    supabase = authenticated_supabase_client()
    user_conversations = load_conversations(supabase)
except Exception:
    clear_session_state()
    st.warning("Your session expired. Please log in again.")
    st.rerun()

render_sidebar(supabase, user_conversations)
render_chat_page(supabase, user_conversations)
