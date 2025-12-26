from contextlib import nullcontext
import pytest
from einsingen.simple.notes import SimpleNote


# test valid notes
@pytest.mark.parametrize(
    "note_value, midi_number, midi_octave, sung_octave",
    [
        (0, 0, -2, -1),
        (60, 60, 3, 4),
        (127, 127, 8, 9),
    ],
)
def test_valid_notes(note_value, midi_number, midi_octave, sung_octave):
    note = SimpleNote.from_int(note_value)
    assert note.midi_number == midi_number
    assert note.midi_octave == midi_octave
    assert note.sung_octave == sung_octave


# test invalid notes
@pytest.mark.parametrize(
    "note_value, exception",
    [
        (-1, pytest.raises(ValueError)),
        (128, pytest.raises(ValueError)),
    ],
)
def test_invalid_notes(note_value, exception):
    with exception:
        SimpleNote.from_int(note_value)


@pytest.mark.parametrize(
    "initial, add, expectation,",
    [
        (60, 12, nullcontext(SimpleNote.from_int(72))),
        (60, -12, nullcontext(SimpleNote.from_int(48))),
        (24, -36, pytest.raises(ValueError)),
        (96, +36, pytest.raises(ValueError)),
    ],
)
def test_add(initial, add, expectation):
    note = SimpleNote.from_int(initial)
    with expectation as e:
        assert note + add == e


@pytest.mark.parametrize(
    "initial, sub, expectation,",
    [
        (60, 12, nullcontext(SimpleNote.from_int(48))),
        (60, -12, nullcontext(SimpleNote.from_int(72))),
        (96, -36, pytest.raises(ValueError)),
        (24, +36, pytest.raises(ValueError)),
    ],
)
def test_sub(initial, sub, expectation):
    note = SimpleNote.from_int(initial)
    with expectation as e:
        assert note - sub == e


def test_note_int():
    note = SimpleNote.from_int(60)
    assert int(note) == 60
