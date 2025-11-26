from typing import ClassVar, Optional

from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth.models import User
from einsingen.api.auth import SuperUserAuth
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.security import SessionAuth


class CreateUserIn(Schema):
    username: str
    password: str
    email: Optional[str] = None


class UserOut(Schema):
    status: int
    username: str


# TODO: This is not currently needed because the error is raised, not returned.
class Error(Schema):
    success: ClassVar[bool] = False
    status: int
    message: str


class UpdatePasswordIn(Schema):
    username: str
    current_password: str
    new_password: str


class DeleteUserIn(Schema):
    username: str
    password: str


class MessageOut(Schema):
    success: bool
    detail: str


users_router = Router()


@users_router.post("/create", response=UserOut)
def create_user(request, payload: CreateUserIn):
    # check existing
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "User with that username already exists")
    user = User.objects.create_user(username=payload.username, email=payload.email or "", password=payload.password)
    user.save()
    return UserOut(status=201, username=user.username)


@users_router.post("/password", response=UserOut)
def update_password(request, payload: UpdatePasswordIn):
    user = User.objects.filter(username=payload.username).first()
    if not user:
        raise HttpError(404, "User not found")
    # verify current password
    authenticated = django_authenticate(username=payload.username, password=payload.current_password)
    if authenticated is None:
        raise HttpError(403, "Current password is incorrect")
    user.set_password(payload.new_password)
    user.save()
    return UserOut(status=200, username=user.username)


@users_router.post("/delete", response=UserOut, auth=SuperUserAuth())
def delete_user(request, payload: DeleteUserIn):
    user = User.objects.filter(username=payload.username).first()
    if not user:
        raise HttpError(404, "User not found")
    authenticated = django_authenticate(username=payload.username, password=payload.password)
    if authenticated is None:
        raise HttpError(403, "Invalid credentials")
    user.delete()
    return UserOut(status=200, username=user.username)


@users_router.get("/", response=list[dict[str, bool | str]], auth=SuperUserAuth())
def get_all_users(request):
    return ({"username": user.username, "is_superuser": user.is_superuser} for user in User.objects.all())


# Return user if authenticated
@users_router.get("/me", auth=SessionAuth(csrf=False))
def user(request):
    return {"username": request.user.username}
