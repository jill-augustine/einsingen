from fractions import Fraction

import pytest
from einsingen.beats import Beat


@pytest.mark.parametrize(
    "fraction, expectation",
    [
        ("1/32", Fraction(1, 32)),
        ("1/16", Fraction(1, 16)),
        ("1/8", Fraction(1, 8)),
        ("1/4", Fraction(1, 4)),
        ("1/2", Fraction(1, 2)),
        ("1/1", Fraction(1, 1)),
        ("2/1", Fraction(2, 1)),
        ("4/1", Fraction(4, 1)),
        ("8/1", Fraction(8, 1)),
    ],
)
def test_valid_fractions(fraction, expectation):
    assert Beat(fraction).value == expectation


@pytest.mark.parametrize(
    "args, exception",
    [
        (("-1/4",), pytest.raises(ValueError)),
        (("1/0",), pytest.raises(ZeroDivisionError)),
        # Valid but not currently accepted
        (("1/64",), pytest.raises(ValueError)),
        (("16/1",), pytest.raises(ValueError)),
        (("3/4",), pytest.raises(ValueError)),
        (
            tuple([3, 4, 5]),
            pytest.raises(TypeError),
        ),
    ],
)
def test_invalid_fractions(args, exception):
    with exception:
        Beat(*args)


def test_beat_from_float():
    b = Beat(0.25)
    assert b.value == Fraction(1, 4)


def test_beat_from_tuple():
    b = Beat(1, 4)
    assert b.value == Fraction(1, 4)


def test_beat_string():
    b = Beat("1/4")
    assert b.string == "1/4"


def test_beat_repr():
    b = Beat("1/4")
    assert repr(b) == "<Beat: 1/4>"


def test_beat_value_read_only():
    beat = Beat("1/4")
    with pytest.raises(AttributeError):
        beat.value = Fraction(1, 2)


def test_beat_string_read_only():
    beat = Beat("1/4")
    with pytest.raises(AttributeError):
        beat.string = "1/2"
