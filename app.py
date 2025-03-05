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
    st.set_page_config(page_title="TranquiliChat", page_icon="🤖", layout="wide")
    initialize_session_state()

    st.title("🤖 TranquiliChat")
    st.sidebar.title("Settings")

    # Initialize handlers
    audio_handler = AudioHandler()
    model_handler = ModelHandler()
    prompt_templates = PromptTemplates()
    system_prompt = prompt_templates.get_prompt_tips()

    # Input method selection
    input_method = st.sidebar.radio(
        "Choose Input Method",
        ["Text", "Speech"],
        key="input_method"
    )

    # 🟢 **Prompt Template Selection (Move This Above Model Selection)**
    st.sidebar.subheader("Prompt Engineering")
    selected_template = st.sidebar.selectbox(
        "Select Prompt Template",
        list(prompt_templates.get_templates().keys()),
        key="template"
    )

    # 🟢 **Model Selection Based on Input Type & Stress-Related Prompt**
    if selected_template == "Stress and Mental Wellbeing Support":
        recommended_models = ["LLAMA3 Mental LLM","Flan T5 Mental LLM"]
    else:
        recommended_models = model_handler.get_recommended_models(input_method.lower())
        # Remove stress-specific models if not needed
        recommended_models = [
            model for model in recommended_models
            if model not in ["LLAMA3 Mental LLM","Flan T5 Mental LLM"]
        ]

    selected_model = st.sidebar.selectbox(
        "Choose Model",
        recommended_models,
        key="model"
    )

    # Display chat history
    display_chat_history()

    # 🟢 **Text Input Handling**
    if input_method == "Text":
        user_input = st.chat_input("Type your message here...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            final_model = selected_model
            if selected_template == "Stress and Mental Wellbeing Support":
                final_model = st.sidebar.selectbox(
                    "Choose a Mental Health Model",
                    ["LLAMA3 Mental LLM","Flan T5 Mental LLM"],
                    key="stress_support"
                )
            else:
                final_model = selected_model

            # Generate and display response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = model_handler.generate_response(
                        final_model,
                        user_input,
                        system_prompt
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.markdown(response)

    # 🟢 **Speech Input Handling**
    else:
        if st.button("🎤 Start Recording"):
            with st.spinner("Recording..."):
                audio_path = audio_handler.record_audio()  # Save the recorded file

                if audio_path:
                    # Transcribe the recorded audio using Whisper
                    transcribed_text = audio_handler.transcribe(audio_path)  # Ensure this returns text

                    if transcribed_text:
                        st.session_state.messages.append({"role": "user", "content": transcribed_text})
                        with st.chat_message("user"):
                            st.markdown(f"🎤 {transcribed_text}")

                        # 🟢 **Use Mental Health Models If Stress Prompt Is Selected**
                        final_model = selected_model
                        if selected_template == "Stress and Mental Wellbeing Support":
                            final_model = st.sidebar.selectbox(
                                "Choose a Mental Health Model",
                                ["LLAMA3 Mental LLM","Flan T5 Mental LLM"],
                                key="stress_support"
                            )
                        else:
                            final_model = selected_model
                            

                        # Generate response using selected model
                        with st.chat_message("assistant"):
                            with st.spinner("Thinking..."):
                                response = model_handler.generate_response(
                                    final_model,
                                    transcribed_text,
                                    system_prompt
                                )
                                st.session_state.messages.append({"role": "assistant", "content": response})
                                st.markdown(response)

if __name__ == "__main__":
    main()
