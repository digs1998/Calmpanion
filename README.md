
# TranquiliChat

An interactive AI chatbot application powered by multiple language models (Gemini and Llama 3.3) with support for both text and speech input. Work in progress for speech support, stay tuned!!

## Features

- Text-based chat interface
- Speech-to-text input capability
- Multiple AI model support (Gemini Pro and Llama 3.3-70B-Instruct)
- Customizable prompt templates
- System prompt customization options
- Responsive UI built with Streamlit

## Prerequisites

- A Replit account
- API keys for:
  - Google Gemini (for Gemini Pro)
  - Hugging Face (for Llama 3.3 access)

## Setup Instructions

1. **Fork this Repl** to your Replit account

2. **Set up API Keys in Secrets**:
   - Click on the "Secrets" tool in the left sidebar (lock icon)
   - Add the following secrets:
     - `GOOGLE_API_KEY` - Your Google Gemini API key
     - `HUGGINGFACE_API_KEY` - Your Hugging Face API key for accessing Llama 3.3

3. **Run the Application**:
   - Click the "Run" button at the top of the screen
   - The Streamlit application will start automatically and be available in the webview

## Using the Chatbot

1. **Input Method**:
   - Select between "Text" or "Speech" input from the sidebar
   - For speech input, allow microphone access when prompted

2. **Choose an AI Model**:
   - Select "Gemini" or "Llama 3.3" from the dropdown (Speech input only supports Gemini)

3. **Customize Prompts**:
   - Choose from predefined prompt templates in the sidebar
   - Modify the system prompt as needed for different response styles

4. **Interact with the Bot**:
   - For text input: Type your message in the input field at the bottom and press Enter
   - For speech input: Click the "Start Recording" button and speak your query

## Running Locally (outside of Replit)

If you want to run this project locally:

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   or
   ```
   pip install google-generativeai langchain langchain-community huggingface-hub speechrecognition streamlit
   ```
3. Set environment variables for your API keys
4. Run the Streamlit app:
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
