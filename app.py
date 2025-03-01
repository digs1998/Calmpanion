import streamlit as st
from utils.audio_handler import AudioHandler
from utils.model_handler import ModelHandler
from utils.prompt_templates import PromptTemplates

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
    st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")
    initialize_session_state()
    
    st.title("🤖 AI Chatbot")
    st.sidebar.title("Settings")
    
    # Initialize handlers
    audio_handler = AudioHandler()
    model_handler = ModelHandler()
    prompt_templates = PromptTemplates()
    
    # Input method selection
    input_method = st.sidebar.radio(
        "Choose Input Method",
        ["Text", "Speech"],
        key="input_method"
    )
    
    # Model selection based on input type
    recommended_models = model_handler.get_recommended_models(input_method.lower())
    selected_model = st.sidebar.selectbox(
        "Choose Model",
        recommended_models,
        key="model"
    )
    
    # Prompt engineering section
    st.sidebar.subheader("Prompt Engineering")
    selected_template = st.sidebar.selectbox(
        "Select Prompt Template",
        list(prompt_templates.get_templates().keys()),
        key="template"
    )
    
    system_prompt = st.sidebar.text_area(
        "Customize System Prompt",
        value=prompt_templates.get_templates()[selected_template],
        key="system_prompt"
    )
    
    # Display prompt tips
    with st.sidebar.expander("Prompt Engineering Tips"):
        for tip in prompt_templates.get_prompt_tips():
            st.write(f"• {tip}")
    
    # Display chat history
    display_chat_history()
    
    # Input handling
    if input_method == "Text":
        user_input = st.chat_input("Type your message here...")
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Generate and display response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = model_handler.generate_response(
                        selected_model,
                        user_input,
                        system_prompt
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.markdown(response)
    
    else:  # Speech input
        if st.button("🎤 Start Recording"):
            with st.spinner("Recording..."):
                audio_text = audio_handler.record_audio()
                if audio_text:
                    # Add user message to chat
                    st.session_state.messages.append({"role": "user", "content": audio_text})
                    with st.chat_message("user"):
                        st.markdown(f"🎤 {audio_text}")
                    
                    # Generate and display response
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            response = model_handler.generate_response(
                                selected_model,
                                audio_text,
                                system_prompt
                            )
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            st.markdown(response)

if __name__ == "__main__":
    main()
