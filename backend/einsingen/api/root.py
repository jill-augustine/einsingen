# paths defined in einsingen/api/__init__.py
from logging import root
from ninja import Router

from einsingen.api.auth import login, logout
from einsingen.api.melodies import melodies, exercises

root_router = Router()

# Using `Router.get` in functional style instead of decorator so it can wrap functions decalred elsewhere
root_router.get("melodies")(melodies)
root_router.post("exercises")(exercises)
root_router.post("login", auth=None)(login)
root_router.post("logout")(logout)
