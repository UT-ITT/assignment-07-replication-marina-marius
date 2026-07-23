"""
input.py – Raw, unaccelerated mouse delta acquisition.

Provides a unified interface across platforms:
  - macOS  : Core Graphics event tap (bypasses pointer acceleration)
  - Windows / Linux : SDL3 relative mouse mode (SDL3 already bypasses
                      acceleration on these platforms)

Public API
----------
RawMouseInput(window)
    .install()          – start collecting deltas
    .consume() -> (dx, dy)  – return accumulated deltas since last call
    .close()            – clean up

The `window` argument must be a live SDL3 window handle (as returned by
SDL_CreateWindow).  The class is used internally by fitts_law.py; students
do not need to touch this file.
"""

import sys

IS_MACOS = sys.platform == "darwin"

if IS_MACOS:
    import Quartz
    from AppKit import (
        NSEvent,
        NSEventMaskLeftMouseDragged,
        NSEventMaskMouseMoved,
        NSEventMaskOtherMouseDragged,
        NSEventMaskRightMouseDragged,
    )


class _MacRawDeltas:
    """Collect unaccelerated Core Graphics deltas on macOS."""

    def __init__(self) -> None:
        self.dx = 0.0
        self.dy = 0.0
        self._monitor = None

        # kCGEventUnacceleratedPointerMovementX/Y – available macOS 10.15.1+
        self._field_x = getattr(Quartz, "kCGEventUnacceleratedPointerMovementX", 170)
        self._field_y = getattr(Quartz, "kCGEventUnacceleratedPointerMovementY", 171)

    def install(self) -> None:
        mask = (
            NSEventMaskMouseMoved
            | NSEventMaskLeftMouseDragged
            | NSEventMaskRightMouseDragged
            | NSEventMaskOtherMouseDragged
        )

        def _handle(event):
            cg = event.CGEvent()
            if cg is not None:
                self.dx += Quartz.CGEventGetIntegerValueField(cg, self._field_x)
                self.dy += Quartz.CGEventGetIntegerValueField(cg, self._field_y)
            return event  # pass event through so SDL still sees it

        self._monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(mask, _handle)

    def consume(self) -> tuple[float, float]:
        dx, dy = self.dx, self.dy
        self.dx = 0.0
        self.dy = 0.0
        return dx, dy

    def close(self) -> None:
        if self._monitor is not None:
            NSEvent.removeMonitor_(self._monitor)
            self._monitor = None


class _SDLRelativeDeltas:
    """
    Collect deltas from SDL3 relative mouse mode.

    SDL3 on Windows and Linux already bypasses OS pointer acceleration when
    relative mouse mode is active, so no platform-specific workaround is needed.
    """

    def __init__(self) -> None:
        self.dx = 0.0
        self.dy = 0.0

    def install(self) -> None:
        pass  # SDL relative mode is enabled by fitts_law.py at window creation

    def feed(self, dx: float, dy: float) -> None:
        """Call this for every SDL_EVENT_MOUSE_MOTION event."""
        self.dx += dx
        self.dy += dy

    def consume(self) -> tuple[float, float]:
        dx, dy = self.dx, self.dy
        self.dx = 0.0
        self.dy = 0.0
        return dx, dy

    def close(self) -> None:
        pass


class RawMouseInput:
    """
    Unified raw mouse input for macOS, Windows, and Linux.

    Usage
    -----
    raw = RawMouseInput(sdl_window)
    raw.install()

    # inside event loop (non-macOS only – on macOS this is a no-op):
    if event.type == SDL_EVENT_MOUSE_MOTION:
        raw.feed_sdl_motion(event.motion.xrel, event.motion.yrel)

    # once per frame:
    dx, dy = raw.consume()

    raw.close()  # on shutdown
    """

    def __init__(self, window) -> None:
        self._window = window
        if IS_MACOS:
            self._backend = _MacRawDeltas()
        else:
            self._backend = _SDLRelativeDeltas()

    def install(self) -> None:
        self._backend.install()

    def feed_sdl_motion(self, xrel: float, yrel: float) -> None:
        """
        Forward SDL mouse-motion deltas to the backend.
        Only meaningful on non-macOS; safe to call on macOS (no-op).
        """
        if not IS_MACOS:
            self._backend.feed(xrel, yrel)

    def consume(self) -> tuple[float, float]:
        """Return accumulated (dx, dy) since the last call and reset to zero."""
        return self._backend.consume()

    def close(self) -> None:
        self._backend.close()
