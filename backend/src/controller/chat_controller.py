from src.integrations.ollama_client import ollama_client

class ChatController():
    def create_chat_response(self, prompt: str):
        chat_response = ollama_client.generate(prompt)
        return chat_response

chat_controller = ChatController()