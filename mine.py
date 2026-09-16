"""
Step 35: a Mine is a hidden hazard sitting somewhere in the minefield.
It's invisible by default -- draw() only actually draws anything while
self.revealed_timer is above 0, which main.py sets whenever a scan pulse
catches this mine within range. Being invisible doesn't make it safe to
walk into, though: main.py checks mine collision against the player
every frame regardless of whether it's currently visible, same as a real
landmine doesn't care whether you can see it.
"""

import pygame

import settings


class Mine:
    def __init__(self, center):
        self.rect = pygame.Rect(0, 0, settings.MINE_SIZE, settings.MINE_SIZE)
        self.rect.center = center

        # Counts down to 0 every frame (main.py calls update(dt)) --
        # only drawn while this is above 0. Starts at 0 so a fresh mine
        # is invisible until a scan actually finds it.
        self.revealed_timer = 0.0

    @property
    def is_revealed(self):
        return self.revealed_timer > 0

    def reveal(self):
        """Called by main.py's scan handling when this mine falls within
        SCANNER_RADIUS of the player -- makes it visible for
        SCANNER_REVEAL_DURATION seconds from right now."""
        self.revealed_timer = settings.SCANNER_REVEAL_DURATION

    def update(self, dt):
        if self.revealed_timer > 0:
            self.revealed_timer -= dt

    def draw(self, screen, camera_x, camera_y):
        if not self.is_revealed:
            return
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, settings.MINE_COLOR, screen_rect)
        pygame.draw.rect(screen, settings.MINE_BORDER_COLOR, screen_rect, 2)