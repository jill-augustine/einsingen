import django.contrib.auth as auth
from django.contrib.auth.decorators import login_not_required
from ninja.errors import AuthenticationError
from ninja.security import HttpBasicAuth


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = auth.authenticate(
            username=username,
            password=password,
        )
        return user


class SuperUserAuth(HttpBasicAuth):
    def authenticate(self, request, username, password) -> bool:
        user = auth.authenticate(
            username=username,
            password=password,
        )
        return user.is_superuser if user else False


def login(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
        # Redirect to /home is handled on frontend
        return {"username": user.username}
    else:
        raise AuthenticationError


def logout(request):
    auth.logout(request)
