# the run-wide scoreboard: lives on StateManager since that's the one thing
# that survives every set_state() call, so any screen can poke at it via
# self.manager.stats instead of us threading a stats object through everyone
import time


class GameStats:
    def __init__(self):
        self.reset()

    def reset(self):
        self.run_start_time = None
        self.bullets_fired = 0
        self.pitch_attempts = 0
        self.pitch_hits = 0

    def start_run(self):
        # called the moment a run actually begins (start menus 2nd click),
        # not on __init__, so refreshing the app doesn't already have a clock running
        self.reset()
        self.run_start_time = time.time()

    def record_bullet_fired(self):
        self.bullets_fired += 1

    def record_pitch_sample(self, matched):
        # one sample per frame P1 is singing during an actual color-match
        # check (start button, any Gate, any Chest) => Shield/Gun don't have
        # a fixed target to be "right" or "wrong" against, so they don't call this
        self.pitch_attempts += 1
        if matched:
            self.pitch_hits += 1

    def elapsed(self):
        if self.run_start_time is None:
            return 0.0
        return time.time() - self.run_start_time

    def accuracy(self):
        if self.pitch_attempts == 0:
            return 0.0
        return self.pitch_hits / self.pitch_attempts
