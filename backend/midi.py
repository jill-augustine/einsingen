import argparse
from io import BytesIO
from pathlib import Path
import sys

from mido import MidiFile
from einsingen.patterns import MelodyPattern, PitchPattern, RhythmPattern
import einsingen.library as lib

pitch_patterns = {k: v for k, v in vars(lib).items() if isinstance(v, PitchPattern)}

rhythm_patterns = {k: v for k, v in vars(lib).items() if isinstance(v, RhythmPattern)}
parser = argparse.ArgumentParser("Melody Maker")

parser.add_argument("pitch", help="The PitchPattern to use.", default=lib.MAJOR_SCALE)
parser.add_argument("rhythm", help="The RhythmPattern to use.", default=lib.EIGHT_QUARTERS)
parser.add_argument(
    "-o", "--output", type=Path, help="Location to output file. Defaults to stdout.", default=sys.stdout.buffer
)

if __name__ == "__main__":
    args = parser.parse_args()
    melody = MelodyPattern(pitch=lib.MAJOR_SCALE, rhythm=lib.EIGHT_QUARTERS)
    track = melody.to_midi_track()
    file = MidiFile(tracks=[track])
    with BytesIO() as fp:
        file.save(file=fp)
        data = fp.getvalue()
        print("saving")

    print("saved")
