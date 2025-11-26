import json
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

try:
    this_dir = Path(__file__).parent.absolute()
except Exception:
    this_dir = Path().absolute()

with open(this_dir / "midi_notes.json") as fp:
    config = json.load(fp)


@dataclass(eq=True, order=True)
class Note:
    MIN: ClassVar[int] = 0
    MAX: ClassVar[int] = 127
    _value: int
    # later: Add name attribute?

    def __init__(self, value: int) -> None:
        if not self.MIN <= value <= self.MAX:
            raise ValueError(f"Note must fall within valid range ({self.MIN} <= note <= {self.MAX}).")
        self._value = value

    @classmethod
    def is_valid(cls, note: int | Note):
        return cls.MIN <= int(note) <= cls.MAX

    @property
    def value(self) -> int:
        return self._value

    def __repr__(self) -> str:
        return f"<Note:{self.value}>"

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def transpose(self, t) -> Note:
        note = Note(self.value + t)
        if not self.is_valid(note):
            raise ValueError(f"Note {note} falls outside valid range.")
        return note


NOTES = {k: Note(v) for k, v in config["notes"].items()}

# NOTE: Currently using arpeggio slicer but keeping "arp" runs in RUNS for now.
# NOTE: Could also porentially be a class or at least a NamedTuple
# (mood+scale_type, scale|arp, length, asc|desc) cts as pitch templates in PitchPattern.from_template

RUNS = {
    ("major", "scale", 8, "asc"): (0, 2, 4, 5, 7, 9, 11, 12),
    ("natural minor", "scale", 8, "asc"): (0, 2, 3, 5, 7, 8, 10, 12),
    ("harmonic minor", "scale", 8, "asc"): (0, 2, 3, 5, 7, 8, 11, 12),
    ("melodic minor", "scale", 8, "asc"): (0, 2, 3, 5, 7, 9, 11, 12),
    ("melodic minor", "scale", 8, "desc"): (12, 10, 8, 7, 5, 3, 2, 0),
    ("major", "scale", 15, "asc"): (0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24),
    ("natural minor", "scale", 15, "asc"): (0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24),
    ("harmonic minor", "scale", 15, "asc"): (0, 2, 3, 5, 7, 8, 11, 12, 14, 15, 17, 19, 20, 23, 24),
    ("melodic minor", "scale", 15, "asc"): (0, 2, 3, 5, 7, 9, 11, 12, 14, 15, 17, 19, 21, 23, 24),
    ("melodic minor", "scale", 15, "desc"): (24, 22, 20, 19, 17, 15, 14, 12, 10, 8, 7, 5, 3, 2, 0),
    ("major", "arp", 4, "asc"): (0, 4, 7, 12),
    ("natural minor", "arp", 4, "asc"): (0, 3, 7, 12),
    ("harmonic minor", "arp", 4, "asc"): (0, 3, 7, 12),
    ("melodic minor", "arp", 4, "asc"): (0, 3, 7, 12),
    ("major", "arp", 7, "asc"): (0, 4, 7, 12, 16, 19, 24),
    ("natural minor", "arp", 7, "asc"): (0, 3, 7, 12, 15, 19, 24),
    ("harmonic minor", "arp", 7, "asc"): (0, 3, 7, 12, 15, 19, 24),
    ("melodic minor", "arp", 7, "asc"): (0, 3, 7, 12, 15, 19, 24),
}
