

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
        
    def generate(self, prompt: str, as_json=False, extra_messages=None):
        if extra_messages is None:
            extra_messages = []
        opts = {
            'temperature': 0.2,
            'top_p': 0.9,
            'repeat_penalty': 1.05,
            'num_ctx': 8192
        }
        kwargs = {
            'model': 'llama3.1:8b-instruct-q4_K_M',
            'messages': [
                {"role": "system", "content": self.messages[0]['content']},
                *extra_messages,
                {"role": "user", "content": prompt}
            ],
            'options': opts
        }
        if as_json:
            kwargs['as_json'] = True

        response: ChatResponse = chat(**kwargs)
        chat_response = response['message']['content']

        return chat_response


ollama_client = OllamaClient()