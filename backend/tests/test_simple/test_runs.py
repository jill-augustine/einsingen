from re import S
from einsingen.simple.runs import SimplePitchPatternTemplate, SimpleRunPatternTemplate, get_run
from einsingen.simple.notes import SIMPLE_NOTES
import pytest
from contextlib import nullcontext


@pytest.mark.parametrize(
    "ints, expectation",
    [
        ((60, 65, 70), nullcontext(SimplePitchPatternTemplate((0, 5, 10)))),
        ((95, 85, 75), nullcontext(SimplePitchPatternTemplate((0, -10, -20)))),
        ((0, 128), pytest.raises(ValueError)),
        ((60, "a", 70), pytest.raises(TypeError)),
    ],
)
def test_pitch_pattern_template_from_ints(ints, expectation):
    with expectation as e:
        result = SimplePitchPatternTemplate.from_ints(ints)
        assert result == e
        assert result.offsets[0] == 0


@pytest.mark.parametrize(
    "starting_note, expectation",
    [
        (SIMPLE_NOTES[60], nullcontext([SIMPLE_NOTES[60], SIMPLE_NOTES[64], SIMPLE_NOTES[67], SIMPLE_NOTES[72]])),
        (SIMPLE_NOTES[0], nullcontext([SIMPLE_NOTES[0], SIMPLE_NOTES[4], SIMPLE_NOTES[7], SIMPLE_NOTES[12]])),
        (65, pytest.raises(TypeError)),
    ],
)
def test_pitch_pattern_template_apply(starting_note, expectation):
    template = SimplePitchPatternTemplate((0, 4, 7, 12))
    with expectation as e:
        pitch_pattern = template.apply(starting_note)
        assert pitch_pattern.notes == tuple(e)


@pytest.mark.parametrize(
    "other, expectation",
    [
        (SIMPLE_NOTES[60], nullcontext([SIMPLE_NOTES[60], SIMPLE_NOTES[64], SIMPLE_NOTES[67], SIMPLE_NOTES[72]])),
        (SIMPLE_NOTES[0], nullcontext([SIMPLE_NOTES[0], SIMPLE_NOTES[4], SIMPLE_NOTES[7], SIMPLE_NOTES[12]])),
        (65, pytest.raises(TypeError)),
    ],
)
def test_pitch_pattern_template_mul(other, expectation):
    template = SimplePitchPatternTemplate((0, 4, 7, 12))
    with expectation as e:
        pitch_pattern = template * other
        assert pitch_pattern.notes == tuple(e)


@pytest.mark.parametrize(
    "key, value, expectation",
    [
        ("mode", "major", nullcontext()),
        ("mode", "dorian", pytest.raises(ValueError)),
        ("run_type", "scale", nullcontext()),
        ("run_type", "circle_of_fifths", pytest.raises(ValueError)),
        ("direction", "asc", nullcontext()),
        ("direction", "upwards", pytest.raises(ValueError)),
        ("offsets", [0, 2, 4, 5, 7], nullcontext()),
        ("offsets", [0, 2, "a", 5], pytest.raises(TypeError)),
    ],
)
def test_run_pattern_template_from_dict(key, value, expectation):
    kwargs = {
        "mode": "major",
        "run_type": "scale",
        "direction": "asc",
        "offsets": [0, 2, 4, 5, 7],
    }
    kwargs.update({key: value})
    with expectation as e:
        template = SimpleRunPatternTemplate.from_dict(kwargs)
        assert template.mode == kwargs["mode"]
        assert template.run_type == kwargs["run_type"]
        assert template.direction == kwargs["direction"]
        assert template.offsets == tuple(kwargs["offsets"])


@pytest.mark.parametrize(
    "offsets, run_type, expected_length",
    [
        ((0, 2, 4, 5, 7, 9, 11, 12), "scale", 1),
        ((0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24), "scale", 2),
        ((0, 4, 7, 12), "arpeggio", 1),
        ((0, 3, 7, 12, 15, 19, 24), "arpeggio", 2),
    ],
)
def test_n_octaves(offsets, run_type, expected_length):
    template = SimpleRunPatternTemplate(
        mode="major",
        run_type=run_type,
        direction="asc",
        offsets=offsets,
    )
    assert template.n_octaves == expected_length


@pytest.mark.parametrize(
    "offsets, run_type, by, expected_length",
    [
        ((0, 2, 4, 5, 7, 9, 11, 12), "scale", 2, 22),
        ((0, 4, 7, 12), "arpeggio", 3, 13),
    ],
)
def test_extend_octaves_by(offsets, run_type, by, expected_length):
    template = SimpleRunPatternTemplate(
        mode="major",
        run_type=run_type,
        direction="asc",
        offsets=offsets,
    )
    extended = template.extend_octaves(by=by)
    assert extended.n_octaves == by + 1
    assert len(extended) == expected_length


@pytest.mark.parametrize(
    "offsets, run_type, to, expected_length",
    [
        ((0, 2, 4, 5, 7, 9, 11, 12), "scale", 3, 22),
        ((0, 4, 7, 12), "arpeggio", 4, 13),
    ],
)
def test_extend_octaves_to(offsets, run_type, to, expected_length):
    template = SimpleRunPatternTemplate(
        mode="major",
        run_type=run_type,
        direction="asc",
        offsets=offsets,
    )
    extended = template.extend_octaves(to=to)
    assert extended.n_octaves == to
    assert len(extended) == expected_length


def test_run_pattern_template_to_dict():
    template = SimpleRunPatternTemplate(
        mode="major",
        run_type="scale",
        direction="asc",
        offsets=(0, 2, 4, 5, 7, 9, 11, 12),
    )
    d = template.to_dict()
    assert d["mode"] == "major"
    assert d["run_type"] == "scale"
    assert d["direction"] == "asc"
    assert d["offsets"] == (0, 2, 4, 5, 7, 9, 11, 12)


@pytest.mark.parametrize(
    "tonal_pitch, mode, direction, run_type, n_octaves, expectation",
    [
        (SIMPLE_NOTES[60], "major", "asc", "scale", 1, nullcontext([60, 62, 64, 65, 67, 69, 71, 72])),
        (
            SIMPLE_NOTES[24],
            "natural minor",
            "asc",
            "scale",
            2,
            nullcontext([24, 26, 27, 29, 31, 32, 34, 36, 38, 39, 41, 43, 44, 46, 48]),
        ),
        (SIMPLE_NOTES[48], "harmonic minor", "asc", "scale", 1, nullcontext([48, 50, 51, 53, 55, 56, 59, 60])),
        (SIMPLE_NOTES[36], "melodic minor", "desc", "scale", 1, nullcontext([36, 34, 32, 31, 29, 27, 26, 24])),
        (SIMPLE_NOTES[68], "major", "asc", "arpeggio", 2, nullcontext([68, 72, 75, 80, 84, 87, 92])),
        (SIMPLE_NOTES[72], "natural minor", "asc", "arpeggio", 1, nullcontext([72, 75, 79, 84])),
        (SIMPLE_NOTES[90], "harmonic minor", "desc", "arpeggio", 1, nullcontext([90, 85, 81, 78])),
        (SIMPLE_NOTES[53], "melodic minor", "asc", "arpeggio", 2, nullcontext([53, 56, 60, 65, 68, 72, 77])),
        (65, "major", "asc", "scale", 1, pytest.raises(TypeError)),
        (SIMPLE_NOTES[60], "dorian", "asc", "scale", 1, pytest.raises(LookupError)),
    ],
)
def test_get_run(tonal_pitch, mode, direction, run_type, n_octaves, expectation):
    with expectation as e:
        run = get_run(tonal_pitch=tonal_pitch, mode=mode, direction=direction, run_type=run_type, n_octaves=n_octaves)
        assert tuple(int(n) for n in run.notes) == tuple(e)
