# All endpoings that return MelodyOut.

import json
from io import BytesIO
from typing import NamedTuple

from mido import MidiFile
from ninja import Schema
from pydantic import ConfigDict, TypeAdapter

# from .root import root_router
import einsingen.library as lib
from einsingen.patterns import MelodyPattern

from .exercises import get_exercise


class MelodyResponse(Schema):
    model_config = ConfigDict(ser_json_bytes="base64")
    rhythm: str | None
    pitch: str | None
    melody: bytes


def melodies(request, rhythm: str = "a", pitch: str = "b"):
    """
    GET /melodies?rhythm=...&pitch=...
    """
    melody = MelodyPattern(pitch=lib.MAJOR_SCALE, rhythm=lib.EIGHT_QUARTERS)
    data = melody.get_file_bytes()
    resp = MelodyResponse.model_validate(dict(rhythm=rhythm, pitch=pitch, melody=data))
    return resp.model_dump_json()


class Exercise(Schema):
    name: str
    arp: bool


ExercisesList = TypeAdapter(list[Exercise])


def exercises(request):
    # Load form bytestring
    data = json.loads(request.body).get("exercises", [])
    requested_exercises = ExercisesList.validate_python(data)
    melodies = [get_exercise(e.name, arp=e.arp) for e in requested_exercises]
    if len(melodies) < 1:
        raise ValueError("No exercises found")
    melody = melodies[0]
    for m in melodies[1:]:
        melody = melody.concat(m)
    data = melody.get_file_bytes()
    resp = MelodyResponse.model_validate(dict(rhythm=str(melody.rhythm), pitch=str(melody.pitch), melody=data))
    return resp.model_dump_json()
