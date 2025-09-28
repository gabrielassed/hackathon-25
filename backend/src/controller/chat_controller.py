from src.integrations.llm import is_prompt_disclosure_attempt
from src.integrations.ollama_client import ollama_client

class ChatController():
    def create_chat_response(self, prompt: str, as_json=False, extra_messages=None):
        if is_prompt_disclosure_attempt(prompt):
            return "Desculpe, não posso ajudar com isso.", {
                "intent": "blocked",
                "collected": {"specialty": None, "city": None, "doctorId": None, "date": None},
                "missing": [],
                "reply": "Desculpe, não posso ajudar com isso."
            }
        
        intent = ollama_client.classify_intent(prompt, extra_messages=extra_messages or [])
        print(f"Intent classified as: {intent}")

        if intent == "agendar_consulta":
            resp = ollama_client.generate_options(prompt, extra_messages=extra_messages or [])
            return resp["answer"], resp["state"]

        chat_response = ollama_client.generate(prompt, as_json=as_json, extra_messages=extra_messages)
        return chat_response, None

chat_controller = ChatController()