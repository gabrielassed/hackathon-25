from flask import Flask
from flask_cors import CORS

from src.models.settings.connection import db_connection_handler
from src.main.routes.chat_routes import chat_bp

db_connection_handler.connect_to_db()

app = Flask(__name__)
CORS(app)

app.register_blueprint(chat_bp)