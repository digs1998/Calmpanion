import streamlit as st
from utils.audio_handler import AudioHandler
from utils.model_handler import ModelHandler
from utils.prompt_templates import PromptTemplates
from utils.data_handler import setup_database, setup_qachain  # Import RAG setup
import boto3
import os
import json
import hashlib
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client('s3', 
                            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), 
                            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                            region_name=os.getenv("AWS_REGION"),
                            verify=True,
                            use_ssl = True,
                            config=boto3.session.Config(
                                signature_version='s3v4',
                                retries={'max_attempts': 3}
                            ))

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_USERS_KEY='users/credentials.json'

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_model' not in st.session_state:
        st.session_state.current_model = None

def display_chat_history():
    """Display chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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
# S3 Utility Functions
# ======================

def get_users_from_s3() -> dict:
    """
    Load user credentials from S3.
    
    Returns:
        dict: Dictionary containing username-password pairs
    """
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_USERS_KEY)
        users_data = json.loads(response['Body'].read().decode('utf-8'))
        return users_data
    except s3_client.exceptions.NoSuchKey:
        # If file doesn't exist, return empty dict
        return {}
    except Exception as e:
        st.error(f"Error accessing S3: {str(e)}")
        return {}

def save_users_to_s3(users_data: dict) -> bool:
    """
    Save user credentials to S3.
    
    Args:
        users_data (dict): Dictionary containing username-password pairs
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        users_json = json.dumps(users_data)
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=S3_USERS_KEY,
            Body=users_json
        )
        return True
    except Exception as e:
        st.error(f"Error saving to S3: {str(e)}")
        return False

def save_user(username: str, password: str) -> bool:
    """
    Save a new user with a hashed password to S3.

    Args:
        username (str): The user's chosen username
        password (str): The user's plain text password (will be hashed before saving)
        
    Returns:
        bool: True if successful, False otherwise
    """
    users = get_users_from_s3()
    if username not in users:
        users[username] = hash_password(password)
        return save_users_to_s3(users)
    return False

def authenticate(username: str, password: str) -> bool:
    """
    Verify user credentials against S3 stored credentials.

    Args:
        username (str): The username to verify
        password (str): The plain text password to verify

    Returns:
        bool: True if credentials are valid, False otherwise
    """
    users = get_users_from_s3()
    hashed_password = hash_password(password)
    return username in users and users[username] == hashed_password

st.set_page_config(page_title="Calmpanion", page_icon="😌", layout="wide")

def main():
    # Change background color to greyish blue
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

    # Initialize session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

    if not st.session_state["authenticated"]:
        # Show full page HTML when not authenticated
        with open("index.html", "r", encoding="utf-8") as file:
            html_content = file.read()
            st.markdown(
                """
                <style>
                    section.main > div {max-width:100%;padding:0;margin:0}
                    [data-testid="stSidebar"] {display: none}
                </style>
                """,
                unsafe_allow_html=True
            )
            components.html(html_content, height=800, width=None)

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

        st.sidebar.empty()

    else:
        # Main content
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"<h2 style='font-size: 20px; font-weight: bold;'>Welcome, to Calmpanion! 👋</h2>", unsafe_allow_html=True)
        with col2:
            if st.button("Logout", key="logout_button"):
                st.session_state.clear()
                st.rerun()

        # Initialize handlers
        audio_handler = AudioHandler()
        model_handler = ModelHandler()
        prompt_templates = PromptTemplates()
        system_prompt = prompt_templates.get_templates()

        # 🔹 **Initialize RAG database**
        db = setup_database()  # Load ChromaDB

        # Input method selection
        input_method = st.sidebar.radio(
            "Choose Input Method",
            ["Text", "Speech"],
            key="input_method"
        )

        # 🔹 **Prompt Template Selection**
        st.sidebar.subheader("How can I help you?")
        selected_template = st.sidebar.selectbox(
            "Select Prompt Template",
            list(prompt_templates.get_templates().keys()),
            key="template"
        )

        qa_chain = None  # Define outside to avoid scope issues
        selected_model = None  # Define outside to avoid scope issues

        if selected_template == "Stress and Mental Wellbeing Support":
            # model_type = st.sidebar.selectbox(
            #     "Choose a Model for QA Chain:",
            #     ("Mistral", "Llama"),
            #     key="qa_model"  # Unique key
            # )
            model_type = "Llama"
            # Initialize the chosen model in the QA chain
            qa_chain = setup_qachain(db, model_type=model_type)
        else:
            # 🔹 **Model Selection (Only when NOT Stress Management)**
            # selected_model = st.sidebar.selectbox(
            #     "Choose Model",
            #     ["Mistral", "Llama"],
            #     key="model"
            # )
            selected_model = "Mistral"
        user_input = None
        # 🔹 **Text Input Handling**
        if input_method == "Text":
            user_input = st.chat_input("Type your message here...")
        
        # 🔹 **Speech Input Handling**
        elif input_method == "Speech":
            st.subheader("🎤 Speak Now")
            audio_bytes = st.file_uploader("Upload a recorded audio file", type=["wav", "mp3", "ogg"])

            if st.button("Record"):
                audio_bytes = audio_handler.record_audio()
            
            if audio_bytes:
                with st.spinner("Processing Speech..."):
                    user_input = audio_handler.transcribe(audio_bytes)
                    st.write(f"🗣 You said: {user_input}")

        # Process user input (from text or speech)
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # 🔹 **Use RAG if Stress Support is Selected**
            context = None  # Default to None
            if selected_template == "Stress and Mental Wellbeing Support" and qa_chain:
                retrieved_docs = qa_chain.run(user_input)
                context = "\n".join(retrieved_docs)  # Convert retrieved chunks to text
                model_to_use = model_type  # Use QA model
            else:
                model_to_use = selected_model  # Use standard model selection

            # 🔹 **Generate Response**
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
