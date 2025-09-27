

from ollama import chat
from ollama import ChatResponse

class OllamaClient:
    def __init__(self):
        with open('src\integrations\configs\contexto.txt', "r", encoding="utf-8") as f:
            contexto = f.read().strip()

        self.messages = [
            {
                'role': 'system',
                'content': contexto
            }
        ]
        
    def generate(self, prompt:str):
         # adiciona mensagem do usuário
        self.messages.append({"role": "user", "content": prompt})

        # envia todo o histórico ao modelo
        response: ChatResponse = chat(model='llama3.1:8b-instruct-q4_K_M', messages=self.messages)
        chat_response = response['message']['content']

        # adiciona resposta do assistente ao histórico
        self.messages.append({"role": "assistant", "content": chat_response})

        return chat_response


ollama_client = OllamaClient()