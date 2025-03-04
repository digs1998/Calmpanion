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
        
        # Setup Mistral via Hugging Face
        self.mistral = HuggingFaceEndpoint(
            endpoint_url="https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
            huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN", "your-huggingface-api-key"),
            task="text-generation",
            max_new_tokens=100,
            temperature=0.6
        )
        
        ## llama 3.3 needs pro subscription, and llama 3.1 is too large to load, so keeping Mistral for now

    def get_recommended_models(self, input_type: str) -> List[str]:
        """Get recommended models based on input type"""
        # if input_type == "text":
        #     return ["Mistral", "Llama 3.1"]
        # else:  # speech
        return ["Mistral"] 
            
    def generate_response(self, model: str, prompt: str, system_prompt: str = "") -> str:
        """Generate response from selected model"""
        try:
            if model == "Mistral":
                full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt
                response = self.mistral(full_prompt)

            # elif model == "Llama 3.1":
            #     full_prompt = f"<|begin_of_text|><|system|>\n{system_prompt}<|user|>\n{prompt}<|assistant|>\n"
            #     return self.llama(full_prompt)

            else:
                raise ValueError(f"Unknown model: {model}")

            if isinstance(response, dict):  
                response_text = response.get("text") or response.get("response") or next(iter(response.values()), "")
            else:
                response_text = str(response)

            return response_text.strip()

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I encountered an error while processing your request."

