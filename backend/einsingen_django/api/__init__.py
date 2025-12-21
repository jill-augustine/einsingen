# TODO: Prevent app internals being sent in response
from io import BytesIO

from mido import MidiFile
from ninja import NinjaAPI, Router, Schema
from ninja.security import SessionAuth
from pydantic import ConfigDict

from einsingen.library import EIGHT_QUARTERS, MAJOR_SCALE
from einsingen.patterns import MelodyPattern

from .auth import BasicAuth
from .exercises import get_exercise
from .root import root_router
from .sessions import sessions_router
from .users import users_router

api = NinjaAPI(auth=[SessionAuth(csrf=False), BasicAuth()], default_router=root_router)
api.add_router(
    "users",
    users_router,
)
api.add_router(
    "sessions",
    sessions_router,
)
