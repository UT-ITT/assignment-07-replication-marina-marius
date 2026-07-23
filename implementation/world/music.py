# one shared looping background-music player - states call play() with
# their own track on_enter, swapping tracks needs a fresh Player since
# pyglet's queue() only appends, it can't replace what's already loaded
import pyglet

import audio_settings

_player = None
_current_path = None


def _apply_music_volume(value):
    # live-updates volume on change
    if _player is not None:
        _player.volume = value


audio_settings.on_music_volume_changed(_apply_music_volume)


def play(path):
    global _player, _current_path
    if path == _current_path:
        return
    if _player is not None:
        _player.pause()
        _player.delete()
    _player = pyglet.media.Player()
    _player.loop = True
    _player.volume = audio_settings.get_music_volume()
    _player.queue(pyglet.media.load(path))
    _player.play()
    _current_path = path


def stop():
    global _player, _current_path
    if _player is not None:
        _player.pause()
        _player.delete()
        _player = None
    _current_path = None
