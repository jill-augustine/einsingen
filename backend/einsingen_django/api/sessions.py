import json
import logging
import re
from typing import ClassVar, Optional
from uuid import uuid4

import django.contrib.auth as auth
from django.apps import apps
from django.core.exceptions import BadRequest
from ninja import Router, Schema
from ninja.errors import AuthenticationError, HttpError
from ninja.security import SessionAuth
from pydantic import BaseModel, ValidationError

from einsingen_django.api.schemas import format_validation_error

from .auth import SuperUserAuth
from .users import CreateUserRequest, UserOut, _create_user

logging.basicConfig(level=logging.INFO)

# This router handles logging in (creating a session), checking user authentication (getting a session), and logging out
# (deleting a session)
sessions_router = Router()


class CreateSessionRequest(BaseModel):
    username: str
    password: str


@sessions_router.post("", auth=None)
def create_session(request):
    # body must contain both username and password
    try:
        parsed_body = CreateSessionRequest.model_validate_json(request.body)
    except ValidationError as e:
        raise HttpError(400, format_validation_error(e))
    return _create_session(request, username=parsed_body.username, password=parsed_body.password)


def _create_session(request, username: str, password: str):
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        # Redirect to /home is handled on frontend
        return UserOut(username=user.username, options=getattr(user, "options", {})).response(201)
    else:
        raise AuthenticationError


# This validates the user who sent the request by "getting" any existing sessions they might have. GET requests do not have a body.
@sessions_router.get("")
def get_session(request):
    UserOptions = apps.get_model("api.UserOptions")
    if request.user.is_authenticated:
        return UserOut(username=request.user.username, options=getattr(request.user, "options", {})).response(200)
    else:
        raise AuthenticationError


@sessions_router.delete("")
def delete_session(request):
    auth.logout(request)
    return UserOut().response(200)


def create_guest_session(request):
    guest_user_options = dict(is_guest=True)
    # These password is not returned to the user and cannot be used to log in again
    # Set _body attribute on request to bypass read-only request.body property
    credentials = CreateUserRequest(
        username=uuid4().hex,
        password=uuid4().hex,
        options=guest_user_options,
    ).model_dump()

    user = _create_user(**credentials)
    request.user = user
    auth.login(request, user)

    logging.info(f"Created guest user with username: {user.username}")
    return UserOut(username=user.username, options=getattr(user, "options", {})).response(201)
