from langchain.llms import HuggingFaceEndpoint
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_groq import ChatGroq
import os
from typing import List, Union
from dotenv import load_dotenv

load_dotenv()

class ModelHandler:
    def __init__(self):
        self.mistral_api = None
        
    def initialize_mistral(self):
        """Initialize Mistral model via HuggingFace API"""
        mistral_api = ChatGroq(
            model="mixtral-8x7b-32768",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.0,
            max_retries=2
        )
        return mistral_api
        
    def initialize_llama(self):
        llm = ChatGroq(
            model="llama3-70b-8192",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.0,
            max_retries=2
        )
        return llm

    
    def generate_response(self, model: str, prompt: str, system_prompt: str, context: Union[str, None] = None) -> str:
        try:
            full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt
            if context:
                full_prompt = f"{context}\n\n{full_prompt}"  # Append context if applicable

            if model == "Mistral":
                mistral_api = self.initialize_mistral()
                response = mistral_api.invoke(full_prompt)
                return response.content

            elif model == "Llama":
                llm = self.initialize_llama()
                response = llm.invoke(full_prompt)
                return response.content
                    
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