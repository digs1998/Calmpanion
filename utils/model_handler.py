import gradio as gr
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.llms import HuggingFaceEndpoint
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_groq import ChatGroq
import os
from langchain_core.runnables import Runnable
from typing import List, Union

class ModelHandler:
    def __init__(self):
        self.mistral_api = None
        
    def initialize_mistral(self):
        """Initialize Mistral model via HuggingFace API"""
        # mistral_api = HuggingFaceEndpoint(
        #     endpoint_url="https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
        #     huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN", "your_api_key"),
        #     task="text-generation",
        #     max_new_tokens=300,
        #     temperature=0.6
        # )
        # return mistral_api
        mistral_api = ChatGroq(
            model="mixtral-8x7b-32768",
            groq_api_key=os.getenv("GROQ_API_KEY", "your_groq_api_key"),
            temperature=0.0,
            max_retries=2
        )
        return mistral_api
        
    def initialize_llama(self):
        llm = ChatGroq(
            model="llama3-70b-8192",
            groq_api_key=os.getenv("GROQ_API_KEY", "your_groq_api_key"),
            temperature=0.0,
            max_retries=2
        )
        return llm
    
    # def generate_response(self, model: str, prompt: str, system_prompt: str, context: Union[str, None] = None) -> List[str]:
    #     try:
    #         # Build the full prompt, including context only if it's relevant
    #         full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt
    #         if context:
    #             full_prompt = f"{context}\n\n{full_prompt}"  # Append context only if provided
            
    #         # 🔹 **Mistral Model Handling**
    #         if model == "Mistral":
    #             mistral_api = self.initialize_mistral()
    #             response = mistral_api.invoke(full_prompt)
    #             return response
            
    #         # 🔹 **Llama Model Handling**
    #         elif model == "Llama":
    #             llm = self.initialize_llama()
    #             full_prompt = f"<|begin_of_text|><|system|>\n{system_prompt}<|user|>\n{prompt}<|assistant|>\n"
    #             if context:
    #                 full_prompt = f"<|context|>\n{context}\n" + full_prompt  # Include context if applicable
    #             response = llm.invoke(full_prompt)
    #             return response
            
    #         else:
    #             raise ValueError("Unsupported model type. Please choose 'Mistral' or 'Llama'.")

    #     except Exception as e:
    #         return [f"⚠ Error generating response: {str(e)}"]
    
    def generate_response(self, model: str, prompt: str, system_prompt: str, context: Union[str, None] = None) -> str:
        try:
            full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt
            if context:
                full_prompt = f"{context}\n\n{full_prompt}"  # Append context if applicable

            if model == "Mistral":
                mistral_api = self.initialize_mistral()
                response = mistral_api.invoke(full_prompt)
                
                if isinstance(response, dict):
                    return response.get("content")
                return str(response)

            elif model == "Llama":
                llm = self.initialize_llama()
                response = llm.invoke(full_prompt)
                if isinstance(response, dict):
                    return response.get("content")
                return str(response)

            else:
                raise ValueError("Unsupported model type. Please choose 'Mistral' or 'Llama'.")
            

        except Exception as e:
            return f"⚠ Error generating response: {str(e)}"
        
        
def get_recommended_models(self, input_type: str) -> List[str]:
        """Get recommended models based on input type"""
        # if input_type == "text":
        #     return ["Mistral", "Llama 3.1"]
        # else:  # speech
        return ["Mistral", "Llama"] 