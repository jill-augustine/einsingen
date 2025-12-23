import json
import re
from typing import ClassVar, Optional

from django.conf import settings
from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth import get_user_model
from django.core.exceptions import BadRequest
from django.http import Http404
from ninja import Field, ModelSchema, Router, Schema
from ninja.errors import HttpError
from ninja.security import SessionAuth
from pydantic import BaseModel, ValidationError, field_validator

from einsingen_django.api.schemas import ResponseSchema, format_validation_error

from .auth import SuperUserAuth


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str | None = None
    options: dict = Field(default_factory=dict)


class UserOut(ResponseSchema):
    status_code: ClassVar[int] = 200
    username: str = ""
    options: dict = Field(default_factory=dict)

    @field_validator("options", mode="before")
    @classmethod
    def unwrap_options(cls, value):
        if isinstance(value, dict):
            return value
        allowed_keys = ["is_guest"]
        return {k: v for k, v in value.__dict__.items() if k in allowed_keys}


class UpdatePasswordRequest(Schema):
    current_password: str
    new_password: str


users_router = Router()


@users_router.post("", auth=None)
def create_user(request):

    # validation using repeat-password is handled on frontend
    parsed_body = CreateUserRequest.model_validate_json(request.body)
    user = _create_user(
        username=parsed_body.username,
        password=parsed_body.password,
        email=parsed_body.email,
        options=parsed_body.options,
    )
    return UserOut(username=user.username, options=getattr(user, "options", {})).response(201)


def _create_user(username, password, email, options=None):
    UserModel = get_user_model()
    from .models import UserOptions

    if UserModel.objects.filter(username=username).exists():
        raise HttpError(400, "User with that username already exists")
    user = UserModel.objects.create_user(
        username=username,
        password=password,
        email=email,
    )

    if options:
        options = UserOptions(user=user, **options)
        options.save()
        user.options = options
    user.save()
    return user


@users_router.put("/{username}/password", auth=[SessionAuth(csrf=False), SuperUserAuth()])
def update_password(request, username: str):
    UserModel = get_user_model()
    user_sending_request = request.user
    if not (user_sending_request.is_superuser or user_sending_request.username == username):
        raise HttpError(403, "You do not have permission to update this user")

    user_to_update = UserModel.objects.filter(username=username).first()
    if not user_to_update:
        raise HttpError(404, "User not found")

    try:
        parsed_body = UpdatePasswordRequest.model_validate_json(request.body)
    except ValidationError as e:
        raise HttpError(400, format_validation_error(e))
    _ = _update_password(user_to_update, parsed_body.current_password, parsed_body.new_password)

    # TODO: add another endpoint for updating /options
    return UserOut(username=username).response(200)


def _update_password(user, current_password: str, new_password: str):
    # verify current password
    authenticated = django_authenticate(username=user.username, password=current_password)
    if authenticated is None:
        raise HttpError(403, "Current password is incorrect")
    user.set_password(new_password)
    user.save()
    return user


@users_router.delete("/{username}")
def delete_user(request, username: str):
    UserModel = get_user_model()
    user_sending_request = request.user
    if not (user_sending_request.is_superuser or user_sending_request.username == username):
        raise HttpError(403, "You do not have permission to delete this user")

    user_to_delete = UserModel.objects.filter(username=username).first()
    if not user_to_delete:
        raise HttpError(404, "User not found")
    user_to_delete.delete()
    return UserOut(username=username).response(200)


# ----------------------------------------------------


@users_router.get("", response=list[dict[str, bool | str]], auth=SuperUserAuth())
def get_all_users(request):
    return ({"username": user.username, "is_superuser": user.is_superuser} for user in UserModel.objects.all())


# TODO: replace with GET /sessions
# Return user if authenticated
@users_router.get("/me", auth=SessionAuth(csrf=False))
def user(request):
    return {"username": request.user.username}
