
# TranquiliChat

An interactive AI chatbot application powered by multiple language models (Gemini and Llama 3.3) with support for both text and speech input. Work in progress for speech support, stay tuned!!

## Features

- Text-based chat interface
- Speech-to-text input capability
- Multimodal AI model support (Mistral AI, OpenAI whisper (for voice support))
- Customizable prompt templates
- System prompt customization options
- Responsive UI built with Streamlit

## Prerequisites

- A Github, and Streamlit Account
- API keys for:
  - Hugging Face 
  - OpenAI API key

## Setup Instructions

1. **Run the Application**:
   - Click the "Run" button at the top of the screen
   - The Streamlit application will start automatically and be available in the webview

## Using the Chatbot

1. **Input Method**:
   - Select between "Text" or "Speech" input from the sidebar
   - For speech input, allow microphone access when prompted

2. **Choose an AI Model**:
   - Currently only Mistral models are supported, but we are actively working on adding more models soon.

3. **Customize Prompts**:
   - Choose from predefined prompt templates in the sidebar
   - Modify the system prompt as needed for different response styles

4. **Interact with the Bot**:
   - For text input: Type your message in the input field at the bottom and press Enter
   - For speech input: Click the "Start Recording" button and speak your query

## Running Locally (outside of Github)

If you want to run this project locally:

1. Clone the repository
2. Install dependencies:

   ```
   conda create -n <my_env> python=3.11 -y
   conda activate <my_env>
   ```
   Once an environment is setup, run
   ```
   pip install -r requirements.txt
   pip install scipy
   ```
3. To instantiate HuggingFace environment, go to huggingface website, and create an access token. Once you have an access token, run in command line

   ```
   export HUGGINGFACE_API_TOKEN = "your-huggingface-api-key"
   ```
   
4. Set environment variables for your API keys
5. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Project Structure

- `app.py`: Main application file with Streamlit UI
- `utils/`: Helper modules
  - `audio_handler.py`: Handles speech-to-text functionality
  - `model_handler.py`: Manages connections to AI models
  - `prompt_templates.py`: Contains prompt templates and tips

## Contributing

Feel free to fork this project and make improvements or add new features.

## License

This project is available under the MIT License.
