from typing import Dict, List

class PromptTemplates:
    @staticmethod
    def get_templates() -> Dict[str, str]:
        # """Return available prompt templates"""
        base_intro = """You are TranquiliChat, a compassionate mental health assistant.
                        Use the following context to provide empathetic, supportive responses for stress management:

                        {context}

                        User: {question}
                        TranquiliChat: """

        return {
            "General Conversation": "Help with general knowledge questions, do not suggest anything which is not related to general conversation like talking about stress.",
            "Creative Writer": "You are a creative writer. Respond with imaginative and engaging content.",
            "Stress and Mental Wellbeing Support": base_intro + "You will be a friend and companion, offering comfort and guidance."
        }
