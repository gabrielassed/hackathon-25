# app/controllers/chat_controller.py
from pydoc import doc
from flask import Blueprint, request, jsonify
import tempfile
import os
from random import randint
from datetime import datetime

from src.controller.chat_controller import chat_controller
from src.main.http_types.http_request import HttpRequest
from src.integrations.tesseract import extract_text_native, extract_text_ocr
from src.integrations.find_exam import match_exam
from src.models.repository.exam_repository import exam_repository
from src.models.repository.consultation_repository import consultation_repository

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

@chat_bp.route("/", methods=['POST'])
def chat():
    http_request = HttpRequest(body=request.json)
    body = http_request.body 
    prompt = body['message']
    history = body.get('history', [])
    if not prompt:
        return jsonify({"error": "message é obrigatório"}), 400
    
    answer, state = chat_controller.create_chat_response(
        prompt,
        extra_messages=history
    )

    return jsonify({"answer": answer, 'state': state}), 200

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
        protocol_number = str(randint(1000000, 9999999))
        name_splited = text[2].split(':')
        name_patient = name_splited[1].strip()

        extra_ctx = """
            Você é um agente administrativo que processa pedidos de exames/procedimentos.
            Sua função é somente: ler texto fornecido, extrair campos e formatar respostas administrativas (protocolo, lista de exames, prazo de auditoria).
            Não é aconselhamento médico. Nunca recuse tarefas por “informações médicas”, pois não há interpretação clínica aqui.
            Regras:

            Obedeça estritamente aos formatos solicitados.

            Se faltar dado, escreva “Não encontrado”.

            Não invente. Não use markdown.

            Nunca traga avisos de segurança médica; apenas processe os campos administrativos solicitados.
        """

        for exam in exams:

            exam_name = exam['name']
            audit = exam['audit']
            string_exams+= '\n'+exam_name
            current_num = 5 if audit == 'yes' else (10 if audit == 'opme' else 0)
            status = 'Pendente, Aguardando Auditoria de 5 dias' if current_num == 0 else ('Pendente, Aguardando Auditoria de 10 dias' if audit=='opme' else 'Aprovado')

            if current_num > max_audit:
                max_audit = current_num

            exam_repository.insert_exam(protocol_number,exam_name,audit, name_patient, status)
        ia_response = chat_controller.create_chat_response(string_exams +'\n Retorne uma mensagem verbalizando o nome de cada um dos exames no protocolo de número nº'+protocol_number+' e informando que o processo de auditoria será de'+str(max_audit)+' dias (se for 0 dias informar que é imediato)', extra_messages=[{"role": "system", "content": extra_ctx}])

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


@chat_bp.route('/consultation', methods=['POST'])
def schedule_consultation():
    data = request.json

    try:
        specialty = data["specialty"]
        period = data["period"]
        city = data["city"]

        consultation_repository.insert_consultation(city, period, specialty)
        return jsonify({
            "message": "Consulta agendada com sucesso!",
            "specialty": specialty,
            "data_agendamento": period # Enviando a string formatada
        }), 201

    except ValueError:
        # Este erro agora pegaria um formato ISO inválido
        return jsonify({"error": "Formato de data inválido. Use o formato ISO: YYYY-MM-DDTHH:MM:SS"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@chat_bp.route('/consultation', methods=['GET'])
def get_consultations():
    data = request.json
    doctor_id = data['doctor_id']

    list_consultations = consultation_repository.list_consultations(doctor_id)
    return jsonify({"consultations": list_consultations})