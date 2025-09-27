from src.validators.user_creator_validator import user_creator_validator
from src.controllers.interfaces.user_creator_controller import UserCreatorControllerInterface

from .interfaces.view_interface import ViewInterface
from .http_types.http_request import HttpRequest
from .http_types.http_response import HttpResponse


class UserCreatorView(ViewInterface):
    def __init__(self, controller: UserCreatorControllerInterface) -> None:
        self.__controller = controller

    def handle_request(self, request: HttpRequest) -> HttpResponse:
        # valida o payload conforme regras (campos obrigatórios, formatos, etc.)
        user_creator_validator(request)

        user_info = request.body
        body_response = self.__controller.create(user_info)

        return HttpResponse(status_code=201, body=body_response)
