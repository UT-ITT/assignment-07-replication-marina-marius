# shared music/sfx volume state
_music_volume = 0.6
_sfx_volume = 0.6

# volume-change listeners
_music_volume_listeners = []


def get_music_volume():
    return _music_volume


def set_music_volume(value):
    global _music_volume
    _music_volume = max(0.0, min(1.0, value))
    for listener in _music_volume_listeners:
        listener(_music_volume)


def on_music_volume_changed(listener):
    _music_volume_listeners.append(listener)


def get_sfx_volume():
    return _sfx_volume


def set_sfx_volume(value):
    global _sfx_volume
    _sfx_volume = max(0.0, min(1.0, value))
