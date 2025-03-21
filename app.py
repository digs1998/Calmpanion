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
import sqlite3
from datetime import datetime

load_dotenv()
s3_client = boto3.client('s3', 
                            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"), 
                            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                            region_name=os.environ.get("AWS_REGION"),
                            verify=True,
                            use_ssl = True,
                            config=boto3.session.Config(
                                signature_version='s3v4',
                                retries={'max_attempts': 3}
                            ))

FEEDBACK_FILE = '/home/ubuntu/feedbacks.json'
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_USERS_KEY='users/credentials.json'


def init_db():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  feedback TEXT, 
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_feedback(feedback_text):
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute("INSERT INTO feedback (feedback, timestamp) VALUES (?, ?)",
              (feedback_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_model' not in st.session_state:
        st.session_state.current_model = None

def display_chat_history():
    """Display chat history"""
    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
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

def get_conversation_context():
    """Combine all messages in session state to form conversation context"""
    if len(st.session_state.conversation_history) > 0:
        context = "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.conversation_history])
    else:
        return None
    return context
    
def main():
    st.set_page_config(page_title="Calmpanion", page_icon="😌", layout="wide")
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
                            /* Make main content full-width on mobile */
                            section.main > div { max-width: 100%; padding: 0; margin: 0; }

                            /* Hide sidebar for small screens */
                            @media screen and (max-width: 768px) {
                                [data-testid="stSidebar"] { display: none; }
                                .stChatInput { width: 100% !important; }
                            }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

            components.html(
                    html_content,
                    height=800,
                    width=None, # ✅ Keep None to allow auto-scaling
                    scrolling=True
                )

        # st.write("### Login / Sign Up (Optional)")
        # col1, col2 = st.columns(2)

        # # Login Section
        # with col1:
        #     st.subheader("Login")
        #     login_username = st.text_input("Username", key="login_username")
        #     login_password = st.text_input("Password", type="password", key="login_password")

        #     if st.button("Login", key="login_button"):
        #         if authenticate(login_username, login_password):
        #             st.session_state["authenticated"] = True
        #             st.session_state["username"] = login_username
        #             st.success("Logged in successfully!")
        #             st.rerun()
        #         else:
        #             st.error("Invalid username or password")

        # Signup Section
        # with col2:
        #     st.sidebar.subheader("Sign Up")
        #     signup_username = st.text_input("Choose Username", key="signup_username")
        #     signup_password = st.text_input("Choose Password", type="password", key="signup_password")

        #     if st.sidebar.button("Sign Up", key="signup_button"):
        #         if signup_username and signup_password:
        #             if save_user(signup_username, signup_password):
        #                 st.success("Signup successful! Please login.")
        #             else:
        #                 st.error("Username already exists!")
        #         else:
        #             st.error("Please provide both username and password")

        # Skip login option
        if st.sidebar.button("Chat with Calmpanion!", key="guest_button"):
            st.session_state["authenticated"] = True
            st.session_state["username"] = "Guest"
            st.sidebar.success("Welcome ...")
            st.rerun()

        # Empty main area
        st.empty()

    else:
        # Main content
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"<h2 style='font-size: 20px; font-weight: bold;'>Welcome, to Calmpanion! 👋</h2>", unsafe_allow_html=True)
        with col2:
            if st.button("Logout", key="logout_button"):
                st.session_state.clear()
                st.session_state["authenticated"] = False  # Ensure login page is shown
                st.session_state["username"] = None  # Clear username
                st.rerun()

        # Initialize handlers
        audio_handler = AudioHandler()
        model_handler = ModelHandler()
        prompt_templates = PromptTemplates()
        system_prompt = prompt_templates.get_templates()

        # 🔹 **Initialize RAG database**
        db = setup_database()  # Load ChromaDB
        
        init_db() # Initializ

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

       # 🔹 **Feedback Section**
        st.sidebar.subheader("Share Your Thoughts")
        
        # Use a form to handle feedback submission and clearing
        with st.sidebar.form(key="feedback_form", clear_on_submit=True):
            feedback_input = st.text_area(
                "What do you think about Calmpanion?",
                height=100,
                key="feedback_input"
            )
            submit_button = st.form_submit_button("Submit Feedback")

        # Handle form submission
        if submit_button:
            if feedback_input.strip():
                save_feedback(feedback_input)
                st.sidebar.success("Thanks for your feedback!")
            else:
                st.sidebar.warning("Please enter some feedback before submitting.")

        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Hi there, how can I help you today?"}]
        
        # Initialize conversation context
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []

        qa_chain = None  # Define outside to avoid scope issues
        selected_model = None  # Define outside to avoid scope issues

        if selected_template == "Stress and Mental Wellbeing Support":
            model_type = "Llama"
            # Initialize the chosen model in the QA chain
            qa_chain = setup_qachain(db, model_type=model_type)
        else:
            selected_model = "Mistral"
        user_input = None
        
        # Display or clear chat messages
        display_chat_history()
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


        if user_input:
            # Add the user input message to history
            st.session_state.conversation_history.append({"role": "user", "content": user_input})

            # Retrieve conversation context
            context = get_conversation_context()

            # Display the user message immediately
            with st.chat_message("user"):
                st.markdown(user_input)

            # Use RAG if Stress Support is Selected
            if selected_template == "Stress and Mental Wellbeing Support" and qa_chain:
                # Retrieve docs using the QA chain
                retrieved_docs = qa_chain.run(user_input)
                retrieved_context = "\n".join(retrieved_docs)  # Convert retrieved chunks to text
                context = f"{get_conversation_context()}\n{retrieved_context}"  # Combine with conversation history
                model_to_use = model_type  # Use QA model
            else:
                model_to_use = selected_model  # Use standard model selection

            # Generate the assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = model_handler.generate_response(
                        model=model_to_use,
                        prompt=user_input,
                        system_prompt=system_prompt,
                        **({"context": context} if context else {})  # Include context only if it's not None
                    )

                    # Add the assistant response to history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.markdown(response)
                    
if __name__ == "__main__":
    main()
