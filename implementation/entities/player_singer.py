from input import audio_input


def pitch_to_color(pitch):
    min_pitch = 100
    max_pitch = 1000
    normalized_pitch = (pitch - min_pitch) / (max_pitch - min_pitch)
    normalized_pitch = max(0.0, min(1.0, normalized_pitch))

    r = int(normalized_pitch * 255)
    g = 0
    b = int((1 - normalized_pitch) * 255)

    return (r, g, b)


# player class with currently only having a color lol
class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def update_color(self, new_color):
        if new_color is None:
            new_color = pitch_to_color(audio_input.current_frequency)
        self.color = new_color