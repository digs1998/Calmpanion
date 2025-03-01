import os
from typing import Dict, List
import google.generativeai as genai
from langchain.llms import LlamaCpp
import streamlit as st

class ModelHandler:
    def __init__(self):
        self.setup_models()
        
    def setup_models(self):
        """Initialize AI models"""
        # Setup Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "your-api-key"))
        self.gemini = genai.GenerativeModel('gemini-pro')
        
        # Setup Llama
        self.llama = LlamaCpp(
            model_path=os.getenv("LLAMA_MODEL_PATH", "models/llama-2-7b-chat.gguf"),
            temperature=0.7,
            max_tokens=2000,
            top_p=1
        )

    def get_recommended_models(self, input_type: str) -> List[str]:
        """Get recommended models based on input type"""
        if input_type == "text":
            return ["Gemini", "Llama"]
        else:  # speech
            return ["Gemini"]  # Gemini handles speech context better
            
    def generate_response(self, model: str, prompt: str, 
                         system_prompt: str = "") -> str:
        """Generate response from selected model"""
        try:
            if model == "Gemini":
                response = self.gemini.generate_content(
                    f"{system_prompt}\n{prompt}" if system_prompt else prompt
                )
                return response.text
            elif model == "Llama":
                full_prompt = f"{system_prompt}\nUser: {prompt}\nAssistant:"
                return self.llama(full_prompt)
            else:
                raise ValueError(f"Unknown model: {model}")
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."
