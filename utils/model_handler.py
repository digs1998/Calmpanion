import os
import torch
import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.llms import HuggingFaceEndpoint 

class ModelHandler:
    def __init__(self):
        self.models = {}  # Store loaded models to avoid reloading
        self.available_models = {
            "Mistral": "mistralai/Mistral-7B-Instruct-v0.3",
            "LLAMA3 Mental LLM": "klyang/MentaLLaMA-chat-7B",
            "Flan T5 Mental LLM": "NEU-HAI/mental-flan-t5-xxl"
        }
        
        # Hugging Face Endpoint for Mistral API (non-mental-health)
        self.mistral_api = HuggingFaceEndpoint(
            endpoint_url="https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
            huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN", "your-huggingface-api-key"),
            task="text-generation",
            max_new_tokens=300,
            temperature=0.6
        )
    
    def load_model(self, model_name: str):
        """Load model on CPU to optimize memory usage."""
        try:
            if model_name in self.models:
                return self.models[model_name]  # Use cached model if already loaded
            
            model_path = self.available_models.get(model_name)
            if not model_path:
                return None  # Invalid model selection
            
            # For non-mental-health models (Mistral), use Hugging Face endpoint
            if model_name == "Mistral":
                return self.mistral_api  # Use the Hugging Face API directly for Mistral

            # For mental-health models (Mistral Mental LLM and Falcon Mental LLM), load locally
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float32,  # Use float32 for CPU
                low_cpu_mem_usage=True,     # Optimize memory on CPU
                device_map="cpu"            # Force CPU execution
            )
            
            # Create a text generation pipeline
            text_generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0)
            
            self.models[model_name] = text_generator  # Cache model to avoid reloading
            return text_generator

        except Exception as e:
            st.error(f"Error loading {model_name}: {str(e)}")
            return None  

    def get_recommended_models(self, input_type: str):
        """Return available models based on input type."""
        return list(self.available_models.keys())

    def generate_response(self, model_name: str, prompt: str, system_prompt: str = ""):
        """Generate response from the selected model."""
        
        # Check if the model is "Mistral" (non-mental-health-related)
        if model_name == "Mistral":
            full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt
            try:
                # Call the Hugging Face API for Mistral model
                response = self.mistral_api(full_prompt)
                
                if isinstance(response, dict):  
                    response_text = response.get("text") or response.get("response") or next(iter(response.values()), "")
                else:
                    response_text = str(response)
                    return response_text.strip()
                
            except Exception as e:
                st.error(f"Error generating response with HuggingFace API for Mistral: {str(e)}")
                return "⚠ I encountered an error while processing your request."

        # For mental-health models (local loading)
        model_pipeline = self.load_model(model_name)
        
        if not model_pipeline:
            return "⚠ Model not available or failed to load."

        full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt

        try:
            response = model_pipeline(full_prompt, max_new_tokens=300, temperature=0.6)
            return response[0]["generated_text"].strip()
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "⚠ I encountered an error while processing your request."
