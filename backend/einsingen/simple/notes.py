from typing import NamedTuple


NOTE_NAMES = (
    "C",
    "C#/Db",
    "D",
    "D#/Eb",
    "E",
    "F",
    "F#/Gb",
    "G",
    "G#/Ab",
    "A",
    "A#/Bb",
    "B",
)


class SimpleNote(NamedTuple):
    name: str
    midi_octave: int
    midi_number: int

    @property
    def sung_octave(self) -> int:
        return self.midi_octave + 1

    @classmethod
    def from_int(cls, midi_number: int):
        if not isinstance(midi_number, int):
            raise TypeError
        if not 0 <= midi_number < 128:
            raise ValueError

        name = NOTE_NAMES[(midi_number % 12)]
        midi_octave = (midi_number // 12) - 2
        return cls(name=name, midi_number=midi_number, midi_octave=midi_octave)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SimpleNote):
            return False
        return self.midi_number.__eq__(other.midi_number)

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.midi_number.__gt__(other.midi_number)

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.midi_number.__ge__(other.midi_number)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.midi_number.__lt__(other.midi_number)

    def __le__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.midi_number.__le__(other.midi_number)

    def __int__(self) -> int:
        # Used when transposing notes e.g. int(note) + 5
        return self.midi_number

    def __add__(self, other) -> SimpleNote:
        if not isinstance(other, int):
            return NotImplemented
        return self.from_int(int(self).__add__(other))

    def __sub__(self, other) -> SimpleNote:
        if not isinstance(other, int):
            return NotImplemented
        return self.from_int(int(self).__sub__(other))


SIMPLE_NOTES = tuple([SimpleNote.from_int(i) for i in range(128)])
