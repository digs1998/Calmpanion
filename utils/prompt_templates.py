from typing import Dict, List

class PromptTemplates:
    @staticmethod
    def get_templates() -> Dict[str, str]:
        """Return available prompt templates"""
        return {
            "General Conversation": "You are a helpful assistant. Start with mentioning, Hi I am TranquiliChat, how can I help you?.",
            "Technical Expert": "You are a technical expert. Provide detailed, technical explanations.",
            "Creative Writer": "You are a creative writer. Respond with imaginative and engaging content.",
            "Professional Consultant": "You are a professional consultant. Provide clear, actionable advice."
        }
    
    @staticmethod
    def get_prompt_tips() -> List[str]:
        """Return prompt engineering tips"""
        return [
            "Be specific in your questions",
            "Provide context when needed",
            "Break complex questions into smaller parts",
            "Specify the desired format of the response",
            "Use clear and unambiguous language",
            "Don't provide or share links, but do cite your sources when giving an output",
            "Be sympathetic in the conversation",
            "If there is any interesting fact related to the prompt, do share it"
        ]
