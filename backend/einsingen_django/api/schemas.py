# 'schema' to match django ninja naming and to not confuse with django models
from typing import ClassVar, Type

from django.http import HttpResponse, HttpResponseRedirect
from ninja.errors import HttpError
from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails


class ResponseSchema(BaseModel):
    status_code: ClassVar[int]

    def response(self, status_code: int | None = None):
        content = self.model_dump_json()
        status_code = status_code or self.__class__.status_code
        if status_code:
            #  kwarg `status` becomes `self.status_code`
            return HttpResponse(content, content_type="application/json", status=status_code)
        return HttpResponse(content)


def format_validation_error(error) -> str:
    if not isinstance(error, ValidationError):
        raise TypeError

    error_messages = []
    for err in error.errors():
        loc_string = ",".join([str(l) for l in err["loc"]])
        err_string = f"{err['msg']}: {loc_string}"
        error_messages.append(err_string)

    return "\n".join(error_messages)
