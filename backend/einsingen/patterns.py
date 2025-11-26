from io import BytesIO
import itertools as it
import operator
from collections.abc import Iterable, Iterator, Sequence
from typing import TypeAlias

from einsingen.beats import Beat
from einsingen.notes import Note
from mido import Message, MidiFile, MidiTrack
from mido.midifiles.midifiles import DEFAULT_TICKS_PER_BEAT

# NOTE: These are not pydantic/ninja models because they are internal to the backend??

FractionArgs: TypeAlias = str | float | int | tuple[float | int, float | int]


class BasePattern(Sequence):
    _values: tuple

    def __init__(self, values):
        self._values = tuple(values)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, i):
        if isinstance(i, slice):
            cls = self.__class__
            return cls(self._values[i])
        return self._values[operator.index(i)]

    def __iter__(self) -> Iterator:
        return iter(self._values)

    def _validate_type(self, values):
        if not isinstance(values, (Sequence, Iterable)):
            raise TypeError("Values must be a Sequence or Iterable.")

    def repeat[T: BasePattern](self: T, times: int) -> T:
        return self.__class__(it.chain.from_iterable(it.repeat(self, times)))

    def concat[T: BasePattern](self: T, other: T) -> T:
        # This will be a subclass not the actual base pattern in practice
        cls = self.__class__
        if not isinstance(other, cls):
            raise TypeError("Cannot concatenate patterns of different types")
        return cls(it.chain(self, other))


class PitchPattern(BasePattern):
    _values: tuple[Note]
    _range: tuple[Note, Note]

    def __init__(self, notes):
        self._validate_type(notes)
        _notes = [n if isinstance(n, Note) else Note(n) for n in notes]
        assert len(_notes) > 0
        # make immutable by setting as tuple via base class
        super().__init__(_notes)
        self._range = int(min(self)), int(max(self))

    # Alias for the inherited `values` attribute
    @property
    def notes(self) -> tuple[Note]:
        return self._values

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {[note.value for note in self.notes]}>"

    @property
    def range(self) -> tuple[Note, Note]:
        return self._range

    @classmethod
    def from_template(cls, template: Sequence[int], starting_note: int | Note) -> PitchPattern:
        pitch_delta = int(starting_note) - template[0]
        return PitchPattern(x + pitch_delta for x in template)

    def transpose(self, t: int) -> PitchPattern:
        return PitchPattern(n.transpose(t) for n in self)

    def transpose_to_start(self, note: int | Note) -> PitchPattern:
        if isinstance(note, (Note, int)):
            value = int(note)
        else:
            raise ValueError(f"Exptected int or note. Got {type(note)}")
        pitch_delta = self.notes[0].value - value
        return self.transpose(pitch_delta)

    def apply(self, rhythm: RhythmPattern) -> MelodyPattern:
        if not isinstance(rhythm, RhythmPattern):
            raise TypeError("rhythm must be type RhythmPattern")
        return MelodyPattern(pitch=self, rhythm=rhythm)


class RhythmPattern(BasePattern):
    value: tuple[Beat]

    def __init__(self, beats: Iterable[FractionArgs]):
        self._validate_type(beats)
        _beats = []
        for b in beats:
            if isinstance(b, Beat):
                _beats.append(b)
            elif isinstance(b, tuple):
                _beats.append(Beat(*b))
            else:
                _beats.append(Beat(b))
        assert len(_beats) > 0
        # make immutable by setting as tuple via base class
        super().__init__(_beats)

    # Alias for the inherited `values` attribute
    @property
    def beats(self) -> tuple[Beat]:
        return self._values

    def __repr__(self) -> str:
        # use str() to get '1/4' instead of 'Fraction(1/4)'
        return (f"<{self.__class__.__name__}: {[beat.string for beat in self.beats]}>").replace(
            "'", ""
        )  # remove extra quotations around '1/4'

    @property
    def duration(self) -> float:
        total = sum(beat.value for beat in self.beats)
        return total.numerator / total.denominator

    def apply(self, pitch: PitchPattern) -> MelodyPattern:
        if not isinstance(pitch, PitchPattern):
            raise TypeError("pitch must be type PitchPattern")
        return MelodyPattern(pitch=pitch, rhythm=self)


class MelodyPattern(BasePattern):
    _pitch: PitchPattern
    _rhythm: RhythmPattern
    _bpm: int | None  # LATER: Use this somehow?
    expected_kwargs: tuple[str, ...] = ("pitch", "rhythm", "bpm")

    def __init__(
        self,
        /,
        pitch: PitchPattern,
        rhythm: RhythmPattern,
        bpm: int | None = None,
    ):
        if len(pitch) != len(rhythm):
            raise ValueError("`pitch` and `rhythm` must be the length")
        self._pitch = pitch if isinstance(pitch, PitchPattern) else PitchPattern(pitch)
        self._rhythm = rhythm if isinstance(rhythm, RhythmPattern) else RhythmPattern(rhythm)
        self._bpm = bpm

    def __repr__(self):
        return f"<{self.__class__.__name__}: range={self.pitch.range}, duration={self.rhythm.duration} bars>"

    @property
    def pitch(self):
        return self._pitch

    @property
    def rhythm(self):
        return self._rhythm

    @property
    def bpm(self):
        return self._bpm

    def transpose(self, t: int) -> MelodyPattern:
        new_pitch = self.pitch.transpose(t)
        return self.repitch(new_pitch)

    def repitch(self, pitch: PitchPattern) -> MelodyPattern:
        if not isinstance(pitch, PitchPattern):
            pitch = PitchPattern(pitch)
        return MelodyPattern(pitch=pitch, rhythm=self.rhythm, bpm=self.bpm)

    def with_start(self, note: int | Note) -> MelodyPattern:
        return MelodyPattern(pitch=self.pitch.transpose_to_start(note), rhythm=self.rhythm)

    def concat(self, other: MelodyPattern) -> MelodyPattern:
        pitch = self.pitch.concat(other.pitch)
        rhythm = self.rhythm.concat(other.rhythm)
        # LATER: Throw error if bpm is off?
        return MelodyPattern(pitch=pitch, rhythm=rhythm)

    def to_midi_track(self, channel: int = 0, velocity: int = 80, ticks_per_beat=None) -> MidiTrack:
        if ticks_per_beat is None:
            ticks_per_beat = DEFAULT_TICKS_PER_BEAT

        track = []
        for note, beat in zip(self.pitch, self.rhythm):
            msgs = [
                Message("note_on", channel=channel, note=note.value, time=0),
                # -1 to finish the note within the beat (not at the beginning of the next beat)
                # Note for `note_off` messages is ignored.
                # multiply by 4 assuming 1 beat is a quarter note. 1/4 * 4 = 1
                Message("note_off", channel=channel, note=note.value, time=round(beat.value * 4 * ticks_per_beat) - 1),
            ]
            track.extend(msgs)
        return MidiTrack(track)

    def to_midi_file(self) -> MidiFile:
        return MidiFile(tracks=[self.to_midi_track()])

    # Named so for possible future get_track_bytes or get_message_bytes
    def get_file_bytes(self) -> bytes:
        file = self.to_midi_file()
        with BytesIO() as fp:
            file.save(file=fp)
            data = fp.getvalue()
        return data


# pp = PitchPattern([2, 3, 4, 5, 6, 7])
# rp = RhythmPattern([1, 1, "1/2", "1/4", 2, 1])
# mp = MelodyPattern(pitch=pp, rhythm=rp)
# print(pp[4:])
# # print(y.concat(x))
# print("end")
