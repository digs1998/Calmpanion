import streamlit as st
from utils.audio_handler import AudioHandler
from utils.model_handler import ModelHandler
from utils.prompt_templates import PromptTemplates
from utils.data_handler import setup_database, setup_qachain  # Import RAG setup

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


def main():
    st.set_page_config(page_title="TranquiliChat", page_icon="🤖", layout="wide")
    initialize_session_state()

    st.title("🤖 TranquiliChat")
    st.sidebar.title("Settings")

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
    st.sidebar.subheader("Prompt Engineering")
    selected_template = st.sidebar.selectbox(
        "Select Prompt Template",
        list(prompt_templates.get_templates().keys()),
        key="template"
    )

    qa_chain = None  # Define outside to avoid scope issues
    selected_model = None  # Define outside to avoid scope issues

    if selected_template == "Stress and Mental Wellbeing Support":
        model_type = st.sidebar.selectbox(
            "Choose a Model for QA Chain:",
            ("Mistral", "Llama"),
            key="qa_model"  # Unique key
        )
        # Initialize the chosen model in the QA chain
        qa_chain = setup_qachain(db, model_type=model_type)
    else:
        # 🔹 **Model Selection (Only when NOT Stress Management)**
        selected_model = st.sidebar.selectbox(
            "Choose Model",
            ["Mistral", "Llama"],
            key="model"
        )
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
