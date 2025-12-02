from einsingen.notes import Note
from einsingen.patterns import MelodyPattern, PitchPattern, RhythmPattern
import pytest

pitch = PitchPattern([60, 64, 67, 72])
rhythm = RhythmPattern(["1/4", "1/8", "1/8", "2/4"])

melody = MelodyPattern(
    pitch=pitch,
    rhythm=rhythm,
)


@pytest.mark.parametrize(
    "pattern1, pattern2",
    [
        # fmt: off
        (pitch, rhythm,), (pitch, melody,),
        (rhythm, pitch,), (rhythm, melody,),
        (melody, pitch,), (melody, rhythm,),
        # fmt: on
    ],
)
def test_mixed_concat(pattern1, pattern2):
    with pytest.raises(TypeError):
        pattern1.concat(pattern2)


def test_concat_pitch():
    pitch1 = PitchPattern([60, 62, 64])
    pitch2 = PitchPattern([65, 67, 69])
    concatenated = pitch1.concat(pitch2)
    assert len(concatenated) == len(pitch1) + len(pitch2)
    assert concatenated == PitchPattern([60, 62, 64, 65, 67, 69])


def test_concat_rhythm():
    rhythm1 = RhythmPattern(["1/4", "1/8"])
    rhythm2 = RhythmPattern(["1/2", "1/4"])
    concatenated = rhythm1.concat(rhythm2)
    assert len(concatenated) == len(rhythm1) + len(rhythm2)
    assert concatenated == RhythmPattern(["1/4", "1/8", "1/2", "1/4"])
    assert concatenated.duration == rhythm1.duration + rhythm2.duration


def test_concat_melody():
    melody1 = MelodyPattern(
        pitch=PitchPattern([60, 62, 64]),
        rhythm=RhythmPattern(["1/4", "1/4", "1/4"]),
    )
    melody2 = MelodyPattern(
        pitch=PitchPattern([65, 67, 69]),
        rhythm=RhythmPattern(["1/8", "1/8", "1/4"]),
    )
    concatenated = melody1.concat(melody2)
    assert len(concatenated.pitch) == len(melody1.pitch) + len(melody2.pitch)
    assert len(concatenated.rhythm) == len(melody1.rhythm) + len(melody2.rhythm)
    assert concatenated.pitch == PitchPattern([60, 62, 64, 65, 67, 69])
    assert concatenated.rhythm == RhythmPattern(["1/4", "1/4", "1/4", "1/8", "1/8", "1/4"])


# transposing keeps all attributes the same except pitch (i.e. length is the same)
@pytest.mark.parametrize(
    "original_pitch, transpose_by,expected,",
    [
        (PitchPattern([60, 62, 64, 65, 67]), 12, PitchPattern([72, 74, 76, 77, 79])),
        (PitchPattern([72, 71, 69, 67, 65]), -12, PitchPattern([60, 59, 57, 55, 53])),
    ],
)
def test_transpose_pitch_in_range(original_pitch, transpose_by, expected):
    transposed = original_pitch.transpose(transpose_by)
    assert transposed == expected
    assert len(transposed) == len(original_pitch)
    assert list(transposed.range) == sorted([expected[0], expected[-1]])


def test_transpose_pitch_out_of_range():
    original_pitch = PitchPattern([120, 122, 124])
    with pytest.raises(ValueError):
        original_pitch.transpose(10)


def test_transpose_pitch_to_start():
    original_pitch = PitchPattern([60, 62, 64, 65, 67])
    transposed = original_pitch.transpose_to_start(65)
    assert transposed[0] == Note(65)
    assert list(transposed.range) == [Note(65), Note(72)]


# TODO: Double or half RhythmPattern?


def test_transpose_melody():
    original_melody = MelodyPattern(pitch=pitch, rhythm=rhythm)
    transposed_melody = original_melody.transpose(12)
    assert transposed_melody.pitch == pitch.transpose(12)
    assert transposed_melody.rhythm == original_melody.rhythm
    assert transposed_melody.bpm == original_melody.bpm


def test_transpose_melody_to_start():
    original_melody = MelodyPattern(pitch=pitch, rhythm=rhythm)
    transposed_melody = original_melody.with_start(65)
    assert transposed_melody.pitch[0] == Note(65)
    assert transposed_melody.rhythm == original_melody.rhythm
    assert transposed_melody.bpm == original_melody.bpm


def test_repitch_melody():
    original_melody = MelodyPattern(pitch=pitch, rhythm=rhythm)
    new_pitch = PitchPattern([65, 69, 72, 77])
    repitched_melody = original_melody.repitch(new_pitch)
    assert repitched_melody.pitch == new_pitch
    assert repitched_melody.rhythm == original_melody.rhythm
    assert repitched_melody.bpm == original_melody.bpm


def test_repitch_melody_invalid_rhythm():
    original_melody = MelodyPattern(pitch=pitch, rhythm=rhythm)
    new_pitch = PitchPattern([65, 69])  # shorter length
    with pytest.raises(ValueError):
        original_melody.repitch(new_pitch)


def test_repeat_pitch():
    original_pitch = PitchPattern([60, 62, 64])
    repeated_pitch = original_pitch.repeat(2)
    assert len(repeated_pitch) == len(original_pitch) * 2
    assert repeated_pitch == PitchPattern([60, 62, 64, 60, 62, 64])


def test_repeat_rhythm():
    original_rhythm = RhythmPattern(["1/4", "1/8"])
    repeated_rhythm = original_rhythm.repeat(3)
    assert len(repeated_rhythm) == len(original_rhythm) * 3
    assert repeated_rhythm == RhythmPattern(["1/4", "1/8", "1/4", "1/8", "1/4", "1/8"])


def test_repeat_melody():
    original_melody = MelodyPattern(pitch=pitch, rhythm=rhythm)
    repeated_melody = original_melody.repeat(3)
    assert len(repeated_melody.pitch) == len(original_melody.pitch) * 3
    assert len(repeated_melody.rhythm) == len(original_melody.rhythm) * 3
    assert repeated_melody.bpm == original_melody.bpm


@pytest.mark.parametrize(
    "rhythm_values, expected_duration",
    [
        (["1/4", "1/4", "1/4", "1/4"], 1.0),
        (["1/8", "1/8", "1/4", "1/2"], 1.0),
        (["1/2", "1/2", "4/4", "1/2"], 2.5),
        (["1/4", "1/8", "1/8"], 0.5),
    ],
)
def test_rhythm_duration(rhythm_values, expected_duration):
    rhythm = RhythmPattern(rhythm_values)
    assert rhythm.duration == expected_duration
