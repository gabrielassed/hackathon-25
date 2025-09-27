# app/controllers/chat_controller.py
from flask import Blueprint, request, jsonify


from src.controller.chat_controller import chat_controller
from src.main.http_types.http_request import HttpRequest


chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

@chat_bp.route("/", methods=['POST'])
def chat():
    http_request = HttpRequest(body=request.json)
    body = http_request.body 
    prompt = body['message']
    if not prompt:
        return jsonify({"error": "message é obrigatório"}), 400
    
    chat_response = chat_controller.create_chat_response(prompt)

    return jsonify({"answer": chat_response})


