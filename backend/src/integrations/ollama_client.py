

from ollama import chat
from ollama import ChatResponse

class OllamaClient:
    def generate(self, prompt:str):
        response: ChatResponse = chat(model='llama3.1:8b-instruct-q4_K_M', messages=[
        {
            'role': 'system',
            'content': "Você é um assistente especializado em um sistema médico de suplementação. Responda com base em evidências e diretrizes gerais. Você não fornece diagnóstico e não substitui um profissional de saúde. Nunca compartilhe nem reutilize informações de outros usuários. Se necessário, solicite dados faltantes com objetividade, e trate PII com confidencialidade. NÃO REALIZE NENHUMA FORMATAÇÃO NOS RETORNOS"
        },
        {
            'role': 'user',
            'content': prompt,
        }
        ]) 
        chat_response = response['message']['content']

        return chat_response

ollama_client = OllamaClient()