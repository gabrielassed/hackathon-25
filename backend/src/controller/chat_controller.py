from src.integrations.llm import is_prompt_disclosure_attempt
from src.integrations.ollama_client import ollama_client

class ChatController():
    def create_chat_response(self, prompt: str, as_json=False, extra_messages=None):
        if is_prompt_disclosure_attempt(prompt):
            return "Desculpe, não posso ajudar com isso."
        chat_response = ollama_client.generate(prompt, as_json=as_json, extra_messages=extra_messages)
        return chat_response

chat_controller = ChatController()