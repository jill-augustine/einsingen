from typing import Literal, Iterable, NamedTuple, Sequence

from .notes import SimpleNote


class SimplePitchPattern(NamedTuple):
    notes: tuple[SimpleNote, ...]

    @classmethod
    def from_notes(cls, notes: Iterable[SimpleNote]) -> SimplePitchPattern:
        if not all(isinstance(n, SimpleNote) for n in notes):
            raise TypeError
        return cls(tuple(notes))


class SimplePitchPatternTemplate(NamedTuple):
    """A pitch pattern template is a collection if integer offsets that can be applied given a starting note.
    The pattern template always starts with 0
    """

    offsets: tuple[int, ...]

    @classmethod
    def from_ints(cls, offsets: Sequence[int]) -> SimplePitchPatternTemplate:
        if not all(isinstance(o, int) for o in offsets):
            raise TypeError
        if max(offsets) - min(offsets) >= 128:
            raise ValueError
        start = offsets[0]
        return cls(tuple(o - start for o in offsets))

    def apply(self, starting_note: SimpleNote) -> SimplePitchPattern:
        if not isinstance(starting_note, SimpleNote):
            raise TypeError
        return SimplePitchPattern.from_notes([starting_note + o for o in self.offsets])

    def __mul__(self, other: object):
        if not isinstance(other, SimpleNote):
            return NotImplemented
        return self.apply(other)


run_pattern_template_dict = [
    {"mode": "major", "run_type": "scale", "direction": "asc", "offsets": (0, 2, 4, 5, 7, 9, 11, 12)},
    {"mode": "major", "run_type": "scale", "direction": "desc", "offsets": (12, 11, 9, 7, 5, 4, 2, 0)},
    {"mode": "natural minor", "run_type": "scale", "direction": "asc", "offsets": (0, 2, 3, 5, 7, 8, 10, 12)},
    {"mode": "natural minor", "run_type": "scale", "direction": "desc", "offsets": (12, 10, 8, 7, 5, 3, 2, 0)},
    {"mode": "harmonic minor", "run_type": "scale", "direction": "asc", "offsets": (0, 2, 3, 5, 7, 8, 11, 12)},
    {"mode": "harmonic minor", "run_type": "scale", "direction": "desc", "offsets": (12, 11, 8, 7, 5, 3, 2, 0)},
    {"mode": "melodic minor", "run_type": "scale", "direction": "asc", "offsets": (0, 2, 3, 5, 7, 9, 11, 12)},
    {"mode": "melodic minor", "run_type": "scale", "direction": "desc", "offsets": (12, 10, 8, 7, 5, 3, 2, 0)},
    {"mode": "major", "run_type": "arpeggio", "direction": "asc", "offsets": (0, 4, 7, 12)},
    {"mode": "major", "run_type": "arpeggio", "direction": "desc", "offsets": (12, 7, 4, 0)},
    {"mode": "natural minor", "run_type": "arpeggio", "direction": "asc", "offsets": (0, 3, 7, 12)},
    {"mode": "natural minor", "run_type": "arpeggio", "direction": "desc", "offsets": (12, 7, 3, 0)},
    {"mode": "harmonic minor", "run_type": "arpeggio", "direction": "asc", "offsets": (0, 3, 7, 12)},
    {"mode": "harmonic minor", "run_type": "arpeggio", "direction": "desc", "offsets": (12, 7, 3, 0)},
    {"mode": "melodic minor", "run_type": "arpeggio", "direction": "asc", "offsets": (0, 3, 7, 12)},
    {"mode": "melodic minor", "run_type": "arpeggio", "direction": "desc", "offsets": (12, 7, 3, 0)},
]


class SimpleRunPatternTemplate(NamedTuple):
    """A run pattern template is a collection if integer offsets with a certain character, e.g. direction, that can be
    applied given a starting note.
    """

    mode: Literal["major", "melodic minor", "natural minor", "harmonic minor"]
    run_type: Literal["scale", "arpeggio"]
    direction: Literal["asc", "desc"]
    offsets: tuple[int, ...]

    def __len__(self):
        return len(self.offsets)

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "run_type": self.run_type,
            "direction": self.direction,
            "offsets": tuple(int(n) for n in self.offsets),
        }

    @classmethod
    def from_dict(cls, d) -> SimpleRunPatternTemplate:
        mode = d.get("mode")
        if mode not in ["major", "melodic minor", "natural minor", "harmonic minor"]:
            raise ValueError

        run_type = d.get("run_type")
        if run_type not in ["scale", "arpeggio"]:
            raise ValueError

        direction = d.get("direction")
        if direction not in ["asc", "desc"]:
            raise ValueError

        offsets = d.get("offsets")
        if not all(isinstance(o, int) for o in offsets):
            raise TypeError

        return cls(mode=mode, run_type=run_type, direction=direction, offsets=tuple(offsets))

    @property
    def octave_length(self) -> int:
        if self.run_type == "scale":
            return 12
        elif self.run_type == "arpeggio":
            return 4
        else:
            raise ValueError(f"Invalid run_type: {self.run_type}")

    @property
    def n_octaves(self) -> int:
        if self.run_type == "scale":
            # subtract 1 starting note, 7 notes per scale
            return int((len(self) - 1) / 7)
        elif self.run_type == "arpeggio":
            return int((len(self) - 1) / 3)
        else:
            raise ValueError(f"Invalid run_type: {self.run_type}")

    def extend_octaves(self, to: int = 0, by: int = 0) -> SimpleRunPatternTemplate:
        # NOTE: Possible TODO, method to reduce length of run.
        if to and by:
            raise ValueError("Either `to` or `by` should be set. Not both.")

        if not (to or by):
            raise ValueError("One of `to` or `by` should be set.")

        if to:
            by = to - self.n_octaves

        offsets = list(self.offsets)
        for _ in range(by):
            last_offset = offsets[-1]
            # `offsets` increases in length each iteration but self.offsets remains the same
            offsets_tmp = [o + last_offset for o in self.offsets]
            # [1:] to exclude the first offset of the template pattern because it was the last offset of the existing run
            offsets.extend(offsets_tmp[1:])

        return self.__class__(mode=self.mode, run_type=self.run_type, direction=self.direction, offsets=tuple(offsets))


# All RUNS for 1 octave and call be extended using Run.extend_octaves()
RUN_PATTERN_TEMPLATES = [SimpleRunPatternTemplate.from_dict(d) for d in run_pattern_template_dict]


def get_run(tonal_pitch: SimpleNote, mode, run_type, direction, n_octaves: int = 1) -> SimplePitchPattern:
    run_pattern_template = [
        r for r in RUN_PATTERN_TEMPLATES if r.mode == mode and r.run_type == run_type and r.direction == direction
    ]
    if len(run_pattern_template) != 1:
        raise LookupError(f"A single matching run template not found. Found: {len(run_pattern_template)}")
    else:
        run_pattern_template = run_pattern_template[0]

    if n_octaves > 1:
        run_pattern_template = run_pattern_template.extend_octaves(to=n_octaves)

    # Create a template that can have a tonal_pitch applied
    template = SimplePitchPatternTemplate.from_ints(run_pattern_template.offsets)

    return template.apply(tonal_pitch)
