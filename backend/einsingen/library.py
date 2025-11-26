from einsingen.patterns import PitchPattern, RhythmPattern

# --- 1-Octave Scales ---
MAJOR_SCALE = PitchPattern([60, 62, 64, 65, 67, 69, 71, 72])
NATURAL_MINOR_SCALE = PitchPattern([60, 62, 63, 65, 67, 68, 70, 72])
HARMONIC_MINOR_SCALE = PitchPattern([60, 62, 63, 65, 67, 68, 71, 72])
MELODIC_MINOR_ASC = PitchPattern([60, 62, 63, 65, 67, 69, 71, 72])
MELODIC_MINOR_DESC = PitchPattern([60, 58, 56, 55, 53, 51, 50, 48])

# --- 2-Octave Scales ---
MAJOR_SCALE_2OCT = PitchPattern(MAJOR_SCALE[:-1]).concat(MAJOR_SCALE.transpose(12))

NATURAL_MINOR_SCALE_2OCT = NATURAL_MINOR_SCALE[:-1].concat(NATURAL_MINOR_SCALE.transpose(12))
HARMONIC_MINOR_SCALE_2OCT = HARMONIC_MINOR_SCALE[:-1].concat(HARMONIC_MINOR_SCALE.transpose(12))
MELODIC_MINOR_ASC_2OCT = MELODIC_MINOR_ASC[:-1].concat(MELODIC_MINOR_ASC.transpose(12))
MELODIC_MINOR_DESC_2OCT = MELODIC_MINOR_DESC[:-1].concat(MELODIC_MINOR_DESC.transpose(-12))

# --- 1-Octave Arpeggios ---
MAJOR_ARP = PitchPattern([60, 64, 67, 72])  # C–E–G–C
NATURAL_MINOR_ARP = HARMONIC_MINOR_ARP = MELODIC_MINOR_ARP = PitchPattern([60, 63, 67, 72])  # C–E♭–G–C

# --- 2-Octave Arpeggios ---
MAJOR_ARP_2OCT = PitchPattern([60, 64, 67, 72, 76, 79, 84])
NATURAL_MINOR_ARP_2OCT = HARMONIC_MINOR_ARP_2OCT = MELODIC_MINOR_ARP_2OCT = PitchPattern([60, 63, 67, 72, 75, 79, 84])

EIGHT_QUARTERS = RhythmPattern("1/4" for _ in range(8))
FIFTEEN_QUARTERS = RhythmPattern("1/4" for _ in range(8))
