# paths defined in einsingen/api/__init__.py
from logging import root

from ninja import Router

from .auth import login, logout
from .melodies import exercises, melodies
from .sessions import create_guest_session

root_router = Router()

# Using `Router.get` in functional style instead of decorator when wrapping functions decalred elsewhere
root_router.get("melodies")(melodies)
root_router.post("exercises")(exercises)
root_router.post("login", auth=None)(login)
root_router.post("logout")(logout)
root_router.post("guest_sessions", auth=None)(create_guest_session)


@root_router.get("health", auth=None)
def health_check(request):
    return {"status": "ok"}
