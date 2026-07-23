# Harmonionz pitch-to-color mapping
import colorsys
import math

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
_A4_FREQUENCY = 440.0
_A4_NOTE_INDEX = NOTE_NAMES.index("A")


def frequency_to_note_index(frequency):
    # nearest semitone, C-indexed
    if frequency <= 0:
        return None
    semitones_from_a4 = 12 * math.log2(frequency / _A4_FREQUENCY)
    return (round(semitones_from_a4) + _A4_NOTE_INDEX) % len(NOTE_NAMES)


def note_index_to_color(note_index):
    # the paper's "mapping value ranging from 0 to 1" -> RGB step
    mapping_value = note_index / len(NOTE_NAMES)
    r, g, b = colorsys.hsv_to_rgb(mapping_value, 1.0, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)


def frequency_to_note_color(frequency, silence_color=(120, 120, 120)):
    # frequency to RGB, one call
    note_index = frequency_to_note_index(frequency)
    if note_index is None:
        return silence_color
    return note_index_to_color(note_index)


def note_index_to_bucket(note_index, bucket_count):
    # equal-width bucket arcs
    notes_per_bucket = len(NOTE_NAMES) / bucket_count
    # center bucket 0 on C
    return int((note_index + notes_per_bucket / 2) // notes_per_bucket) % bucket_count
