import streamlit as st
import os
import sys
import logging
from utils.audio_handler import AudioHandler
from utils.model_handler import ModelHandler
from utils.prompt_templates import PromptTemplates
from utils.data_handler import setup_database, setup_qachain
import json
import hashlib

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("dotenv not installed; using environment variables as-is")

# Simplified user storage for demo purposes (in production, use proper database/S3)
USERS = {}

def hash_password(password: str) -> str:
    """
    Convert a plain text password into a hashed version using SHA-256.

    Args:
        password (str): The plain text password to hash

    Returns:
        str: The hexadecimal representation of the hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# User Management Functions
# ======================

def get_users() -> dict:
    """
    Get users from memory storage (simplified for demo).
    
    Returns:
        dict: Dictionary containing username-password pairs
    """
    global USERS
    return USERS

def save_users(users_data: dict) -> bool:
    """
    Save users to memory storage (simplified for demo).
    
    Args:
        users_data (dict): Dictionary containing username-password pairs
        
    Returns:
        bool: True if successful, False otherwise
    """
    global USERS
    USERS = users_data
    return True

def save_user(username: str, password: str) -> bool:
    """
    Save a new user with a hashed password.

    Args:
        username (str): The user's chosen username
        password (str): The user's plain text password (will be hashed before saving)
        
    Returns:
        bool: True if successful, False otherwise
    """
    users = get_users()
    if username not in users:
        users[username] = hash_password(password)
        return save_users(users)
    return False

def authenticate(username: str, password: str) -> bool:
    """
    Verify user credentials.

    Args:
        username (str): The username to verify
        password (str): The plain text password to verify

    Returns:
        bool: True if credentials are valid, False otherwise
    """
    # For demo, allow any login with non-empty username and password
    if username and password:
        # Save the credentials for future login attempts
        save_user(username, password)
        return True
    return False

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_model' not in st.session_state:
        st.session_state.current_model = None
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

def display_chat_history():
    """Display chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def main():
    # Set page config
    st.set_page_config(page_title="Calmpanion", page_icon="😌", layout="wide")
    
    # Change background color to match index.html
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #B0C4DE; /* Greyish blue */
        }
        header[data-testid="stHeader"] {
            background-color: #B0C4DE; /* Greyish blue */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    initialize_session_state()

    if not st.session_state["authenticated"]:
        # Login/Signup options
        st.write("### Login / Sign Up (Optional)")
        col1, col2 = st.columns(2)

        # Login Section
        with col1:
            st.subheader("Login")
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", key="login_button"):
                if authenticate(login_username, login_password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = login_username
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        # Signup Section
        with col2:
            st.subheader("Sign Up")
            signup_username = st.text_input("Choose Username", key="signup_username")
            signup_password = st.text_input("Choose Password", type="password", key="signup_password")

            if st.button("Sign Up", key="signup_button"):
                if signup_username and signup_password:
                    if save_user(signup_username, signup_password):
                        st.success("Signup successful! Please login.")
                    else:
                        st.error("Username already exists!")
                else:
                    st.error("Please provide both username and password")

        # Skip login option
        if st.button("Continue as Guest", key="guest_button"):
            st.session_state["authenticated"] = True
            st.session_state["username"] = "Guest"
            st.success("Continuing without login...")
            st.rerun()

    else:
        # Main content
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"<h2 style='font-size: 20px; font-weight: bold;'>Welcome to Calmpanion, {st.session_state['username']}! 👋</h2>", unsafe_allow_html=True)
        with col2:
            if st.button("Logout", key="logout_button"):
                st.session_state.clear()
                st.rerun()

        # Initialize handlers
        audio_handler = AudioHandler()
        model_handler = ModelHandler()
        prompt_templates = PromptTemplates()
        system_prompt = prompt_templates.get_templates()

        # Initialize RAG database
        db = setup_database()  # Load ChromaDB

        # Input method selection
        input_method = st.sidebar.radio(
            "Choose Input Method",
            ["Text", "Speech"],
            key="input_method"
        )

        # Prompt Template Selection
        st.sidebar.subheader("How can I help you?")
        selected_template = st.sidebar.selectbox(
            "Select Prompt Template",
            list(prompt_templates.get_templates().keys()),
            key="template"
        )

        qa_chain = None
        selected_model = None

        if selected_template == "Stress and Mental Wellbeing Support":
            model_type = "Llama"
            # Initialize the chosen model in the QA chain
            qa_chain = setup_qachain(db, model_type=model_type)
        else:
            selected_model = "Mistral"
            
        user_input = None
        # Text Input Handling
        if input_method == "Text":
            user_input = st.chat_input("Type your message here...")
        
        # Speech Input Handling
        elif input_method == "Speech":
            st.subheader("🎤 Speak Now")
            audio_bytes = st.file_uploader("Upload a recorded audio file", type=["wav", "mp3", "ogg"])

            if st.button("Record"):
                audio_bytes = audio_handler.record_audio()
            
            if audio_bytes:
                with st.spinner("Processing Speech..."):
                    user_input = audio_handler.transcribe(audio_bytes)
                    st.write(f"🗣 You said: {user_input}")

        # Display chat history
        display_chat_history()

        # Process user input (from text or speech)
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Use RAG if Stress Support is Selected
            context = None  # Default to None
            if selected_template == "Stress and Mental Wellbeing Support" and qa_chain:
                retrieved_docs = qa_chain.run(user_input)
                context = "\n".join(retrieved_docs)  # Convert retrieved chunks to text
                model_to_use = model_type  # Use QA model
            else:
                model_to_use = selected_model  # Use standard model selection

            # Generate Response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = model_handler.generate_response(
                        model=model_to_use,
                        prompt=user_input,
                        system_prompt=system_prompt,
                        **({"context": context} if context else {})  # Include context only if it's not None
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.markdown(response)

if __name__ == "__main__":
    main()