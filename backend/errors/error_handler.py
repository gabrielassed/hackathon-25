from src.main.http_types.http_response import HttpResponse
from .error_types.http_bad_request import HttpBadRequestError
from .error_types.http_unprocessable_entity import HttpUnprocessableEntityError
from .error_types.http_not_found import HttpNotFoundError

def handle_error(errors: Exception) -> HttpResponse:
    if isinstance(errors, (HttpBadRequestError, HttpNotFoundError, HttpUnprocessableEntityError)):
        return HttpResponse(
            status_code= errors.status_code,
            body={
                "errors":[{
                    "title": errors.name,
                    "detail": errors.message,
                }]
            }
        )

    return HttpResponse(
        status_code=500,
        body={
            "error": [{
                "title": "Internal Server Error",
                "detail": str(errors)
            }]
        }
    )