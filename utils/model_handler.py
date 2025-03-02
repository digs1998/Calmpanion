import os
from typing import Dict, List
import google.generativeai as genai
from langchain.llms import HuggingFaceEndpoint
import streamlit as st
import whisper
from utils.audio_handler import AudioHandler

class ModelHandler:
    def __init__(self):
        self.setup_models()
        
    def setup_models(self):
        """Initialize AI models"""
        # Setup Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "your-api-key"))
        self.gemini = genai.GenerativeModel('gemini-1.5-pro-002')
        
        self.whisper = "Whisper" 

    def get_recommended_models(self, input_type: str) -> List[str]:
        """Get recommended models based on input type"""
        if input_type == "text":
            return ["Gemini", "Llama 3.3"]
        else:  # speech
            return ["Whisper"]
            
    def generate_response(self, model: str, prompt: str, 
                         system_prompt: str = "") -> str:
        """Generate response from selected model"""
        try:
            if model == "Gemini":
                response = self.gemini.generate_content(
                    f"{system_prompt}\n{prompt}" if system_prompt else prompt
                )
                return response.text
            
            elif model == "Whisper":
                # Use AudioHandler to transcribe the speech input
                audio_handler = AudioHandler()
                transcribed_text = audio_handler.transcribe(prompt)  # Assuming `prompt` is the audio file path or audio data

                text_model = "Gemini"
                response = self.gemini.generate_content(f"{system_prompt}\n{transcribed_text}" if system_prompt else transcribed_text)
                return response.text
                
            else:
                raise ValueError(f"Unknown model: {model}")
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."
