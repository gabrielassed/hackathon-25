from src.controller.user_creator_controller import UserCreatorController

from src.main.http_types.http_request import HttpRequest
from src.main.http_types.http_response import HttpResponse


class UserCreatorView():
    def __init__(self, controller: UserCreatorController) -> None:
        self.__controller = controller

    def handle_request(self, request: HttpRequest) -> HttpResponse:
        # valida o payload conforme regras (campos obrigatórios, formatos, etc.)

        user_info = request.body
        body_response = self.__controller.create(user_info)

        return HttpResponse(status_code=201, body=body_response)
