from flask import Blueprint, request, jsonify

user_bp = Blueprint("users", __name__, url_prefix="/users")