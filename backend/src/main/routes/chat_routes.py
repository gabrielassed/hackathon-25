# app/controllers/chat_controller.py
from flask import Blueprint, request, jsonify
import tempfile
import os
from random import randint

from src.controller.chat_controller import chat_controller
from src.main.http_types.http_request import HttpRequest
from src.integrations.tesseract import extract_text_native, extract_text_ocr
from src.integrations.find_exam import match_exam


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

@chat_bp.route('/file', methods=['POST'])
def file_upload():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado na requisição"}), 400
    
    temp_file_path = None

    try:
        file = request.files['file']

        fd, temp_file_path = tempfile.mkstemp()
        os.close(fd)

        file.save(temp_file_path)

        text = extract_text_native(temp_file_path)
        is_any_text = any(bool(line.strip()) for line in text)

        if not is_any_text:
            # Tentar extrair imagens do PDF, e ler via oCR
            text = extract_text_ocr(temp_file_path)

        exams = match_exam(text)

        if not exams:
            return jsonify({"message": "Nenhum exame foi encaminhado no documento, poderia por gentileza encaminhar um documento com exames"})

        string_exams = ''
        max_audit = 0
        protocol_number = str(randint(1000, 1000000))


        for exam in exams:
            string_exams+= '\n'+exam['name']
            current_num = 5 if exam['audit'] == 'yes' else (10 if exam['audit'] == 'opme' else 0)
            if current_num > max_audit:
                max_audit = current_num
            #insert on database
        ia_response = chat_controller.create_chat_response(string_exams + '\n Retorne uma mensagem verbalizando o nome de cada um dos exames no protocolo de número nº'+protocol_number+' e informando que o processo de auditoria será de'+str(max_audit)+' dias')

        # Procurar pela chave 'audit' todos os niveis de auditoria pra ver qual será o tempo necessário

    
        

        return jsonify({'text': text, 'exams': exams, 'answer': ia_response}), 200
    except Exception as e:
        return {'error': str(e)}, 500
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
