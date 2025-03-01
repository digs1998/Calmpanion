
import os
from typing import Dict, List
import google.generativeai as genai
from langchain.llms import HuggingFaceEndpoint
import streamlit as st

class ModelHandler:
    def __init__(self):
        self.setup_models()
        
    def setup_models(self):
        """Initialize AI models"""
        # Setup Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "your-api-key"))
        self.gemini = genai.GenerativeModel('gemini-1.5-pro-002')
        
        # # Setup Llama 3.3 via Hugging Face
        # self.llama = HuggingFaceEndpoint(
        #     endpoint_url="https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct",
        #     huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY", "your-huggingface-api-key"),
        #     task="text-generation",
        #     max_new_tokens=2000,
        #     temperature=0.7,
        #     top_p=1.0
        # )

    def get_recommended_models(self, input_type: str) -> List[str]:
        """Get recommended models based on input type"""
        if input_type == "text":
            return ["Gemini", "Llama 3.3"]
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
            # elif model == "Llama 3.3":
            #     # Format the prompt according to Llama 3.3's expected format
            #     full_prompt = f"<|begin_of_text|><|system|>\n{system_prompt}<|user|>\n{prompt}<|assistant|>\n"
            #     return self.llama(full_prompt)
            else:
                raise ValueError(f"Unknown model: {model}")
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."
