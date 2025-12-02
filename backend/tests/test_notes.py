from contextlib import nullcontext
import pytest
from einsingen.notes import Note


# test valid notes
@pytest.mark.parametrize(
    "note_value, expectation",
    [
        (0, 0),
        (60, 60),
        (127, 127),
    ],
)
def test_valid_notes(note_value, expectation):
    note = Note(note_value)
    assert note.value == expectation


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
        Note(note_value)


@pytest.mark.parametrize(
    "note, expectation",
    [
        (Note(60), True),
        (0, True),
        (127, True),
        (-1, False),
        (128, False),
        (60.5, False),
    ],
)
def test_is_valid(note, expectation):
    assert Note.is_valid(note) == expectation


# Note.value is read-only
def test_note_value_read_only():
    note = Note(60)
    with pytest.raises(AttributeError):
        note.value = 61


@pytest.mark.parametrize(
    "initial, transpose_by, expectation,",
    [
        (60, 12, nullcontext(Note(72))),
        (60, -12, nullcontext(Note(48))),
        (24, -36, pytest.raises(ValueError)),
        (96, +36, pytest.raises(ValueError)),
    ],
)
def test_transpose(initial, transpose_by, expectation):
    note = Note(initial)
    with expectation as e:
        assert note.transpose(transpose_by) == e


def test_note_repr():
    note = Note(60)
    assert repr(note) == "<Note:60>"


def test_note_int():
    note = Note(60)
    assert int(note) == 60


def test_note_float():
    note = Note(60)
    assert float(note) == 60.0


def test_note_from_note():
    original = Note(60)
    copy = Note(original)
    assert copy.value == original.value
    assert copy is not original
