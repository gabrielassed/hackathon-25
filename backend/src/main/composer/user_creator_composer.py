from src.models.repository.user_repository import UserRepository
from src.controller.user_creator_controller import UserCreatorController
from src.view.user_creator_view import UserCreatorView
from src.models.settings.connection import db_connection_handler


def user_creator_composer():
    model = UserRepository(db_connection_handler)
    controller = UserCreatorController(model)
    view = UserCreatorView(controller)