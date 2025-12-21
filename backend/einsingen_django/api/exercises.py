# TODO: Test that regexes work with expected scales
import itertools as it
import re
from typing import Literal

from ninja import Field, Schema
from pydantic import field_validator

from einsingen.notes import NOTES, RUNS
from einsingen.patterns import MelodyPattern, PitchPattern, RhythmPattern

NOTE_REGEX = r"([A-Ga-g])(b|#|nat)?\-?[1-9]"
MOOD_REGEX = r"(major|minor)"

SCALE_TYPE_REGEX = r"((?P<type>melodic|natural|harmonic)_)?"
# No space after SCALE_TYPE_REGEX below because it is already included above
# Full scale pattern + optional final length (8 or 15)
SCALE_REGEX = f"^(?P<note>{NOTE_REGEX})_{SCALE_TYPE_REGEX}(?P<mood>{MOOD_REGEX})(_(?P<length>8|15))?$"


def get_type_mood(data: dict) -> str:
    mood = data["mood"]
    type_ = data.get("type")
    if mood == "major" and type_ is not None:
        raise ValueError("Only minor mood can have a type")
    type_mood = f"{type_} " if type_ else ""
    type_mood += mood
    return type_mood


class RunQuery(Schema):
    note: str
    type: Literal["melodic", "natural", "harmonic"] | None
    mood: Literal["major", "minor"]
    length: int = Field(default=8)
    direction: Literal["asc", "desc"] = "asc"
    type_mood: str = Field(default_factory=lambda data: get_type_mood(data))

    @field_validator("note")
    @classmethod
    def is_valid_note(cls, note: str) -> str:
        if note.capitalize() not in NOTES.keys():
            raise ValueError("Note not in accepted notes")
        return note

    @field_validator("length", mode="before")
    @classmethod
    def is_valid_length(cls, length: int | None) -> int:
        if not length:
            length = int(cls.model_fields["length"].default)
        if length % 7 != 1:
            raise ValueError("Invalid length. Try 8, 15 etc...")
        return length


def get_exercise(run_query_string: str, arp: bool = False) -> MelodyPattern:

    pitch_pattern = get_pitch_pattern_from_run_query(run_query_string)
    if arp:
        pitch_pattern = get_arpeggio(pitch_pattern)
        # Standard rhythm
    rhythm_pattern = RhythmPattern(["1/4" for _ in pitch_pattern])
    return MelodyPattern(pitch=pitch_pattern, rhythm=rhythm_pattern)


def get_pitch_pattern_from_run_query(run_query_string):
    match_result = re.match(
        SCALE_REGEX,
        run_query_string.lower(),
    )
    if not match_result:
        raise ValueError(f"Could not parse fields from string: {run_query_string}")
    match_dict = match_result.groupdict()
    params = RunQuery.model_validate(match_dict)
    pitch_template = RUNS[
        (
            params.type_mood,
            "scale",  # TODO: update runs to keep scales only?
            params.length,
            params.direction,
        )
    ]
    starting_note = NOTES[params.note.capitalize()]
    pitch_pattern = PitchPattern.from_template(pitch_template, starting_note)
    return pitch_pattern


def get_arpeggio(pitch_pattern: PitchPattern) -> PitchPattern:
    """Return the arpeggio equivalent of a scale."""
    n_octaves = len(pitch_pattern) // 7
    indices = it.chain.from_iterable((oct_ * 7, oct_ * 7 + 2, oct_ * 7 + 4) for oct_ in range(0, n_octaves))
    indices = list(indices) + [n_octaves * 7]
    pitch_pattern = PitchPattern([p for i, p in enumerate(pitch_pattern) if i in indices])
    return pitch_pattern
