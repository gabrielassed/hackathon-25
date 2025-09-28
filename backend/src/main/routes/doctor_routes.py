from flask import Blueprint, request, jsonify
from src.models.repository.doctor_repository import doctor_repository

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")

@doctor_bp.route("", methods=['POST'])
def create_doctor():
    body = request.json
    name = body.get('name')
    specialty = body.get('specialty')
    city = body.get('city')

    if not name:
        return jsonify({"error": "name é obrigatório"}), 400
    if not specialty:
        return jsonify({"error": "specialty é obrigatório"}), 400

    try:
        doctor_repository.create_doctor(name, specialty, city)
        return jsonify({"message": "Médico criado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500