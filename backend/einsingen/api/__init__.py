# TODO: Prevent app internals being sent in response
from io import BytesIO

from einsingen.api.root import root_router
from einsingen.api.auth import BasicAuth
from einsingen.api.exercises import get_exercise
from einsingen.api.users import users_router
from einsingen.library import EIGHT_QUARTERS, MAJOR_SCALE
from einsingen.patterns import MelodyPattern
from mido import MidiFile
from ninja import NinjaAPI, Schema
from ninja.security import SessionAuth
from pydantic import ConfigDict

api = NinjaAPI(auth=[SessionAuth(csrf=False), BasicAuth()])
api.add_router(
    "",
    root_router,
)
api.add_router(
    "users",
    users_router,
)
