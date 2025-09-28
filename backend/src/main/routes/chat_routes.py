# app/controllers/chat_controller.py
from flask import Blueprint, request, jsonify
import tempfile
import os
from random import randint

from src.controller.chat_controller import chat_controller
from src.main.http_types.http_request import HttpRequest
from src.integrations.tesseract import extract_text_native, extract_text_ocr
from src.integrations.find_exam import match_exam
from src.models.repository.exam_repository import exam_repository

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
            return jsonify({"answer": "Nenhum exame catalogado foi encaminhado no documento, poderia por gentileza encaminhar um documento com exames catalogados"})

        string_exams = ''
        max_audit = 0
        protocol_number = str(randint(1000, 1000000))
        name_splited = text[2].split(':')
        name_patient = name_splited[1].strip()

        for exam in exams:
            exam_name = exam['name']
            audit = exam['audit']
            string_exams+= '\n'+exam_name
            current_num = 5 if audit == 'yes' else (10 if audit == 'opme' else 0)
            status = 'Pendente, Aguardando Auditoria de 5 dias' if current_num == 0 else ('Pendente, Aguardando Auditoria de 10 dias' if audit=='opme' else 'Aprovado')
            if current_num > max_audit:
                max_audit = current_num
            exam_repository.insert_exam(protocol_number,exam_name,audit, name_patient, status)
        ia_response = chat_controller.create_chat_response(string_exams +'\n Retorne uma mensagem verbalizando o nome de cada um dos exames no protocolo de número nº'+protocol_number+' e informando que o processo de auditoria será de'+str(max_audit)+' dias (se for 0 dias informar que é imediato)')

        # Procurar pela chave 'audit' todos os niveis de auditoria pra ver qual será o tempo necessário

    
        

        return jsonify({'text': text, 'exams': exams, 'answer': ia_response}), 200
    except Exception as e:
        return {'error': str(e)}, 500
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)



@chat_bp.route('/context', methods=['GET'])
def return_context():
    """
    Rota para retornar o contexto salvo atualmente
    """
    file_path = os.path.join("src", "integrations", "configs", "contexto.txt")
    
    if not os.path.exists(file_path):
        return jsonify({"error": "Arquivo não encontrado"}), 404

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return jsonify({"context": content})

@chat_bp.route('/context', methods=['POST'])
def save_context():
    """
    Rota para salvar um novo contexto a partir de uma requisição POST
    """
    file_path = os.path.join("src", "integrations", "configs", "contexto.txt")

    data = request.json
    if "context" not in data:
        return jsonify({"error": "Campo 'contexto' é obrigatório"}), 400

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data["context"])

    return jsonify({"success": True, "message": "Contexto salvo com sucesso"})