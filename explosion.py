"""
Step 38: a brief animated flash played wherever a mine actually detonates
(the player walked into it) -- NOT wherever one gets safely defused with
F, since defusing is meant to stay the quiet "you did it right" outcome.

Loads the three frame images (settings.EXPLOSION_FRAME_PATHS) once, the
first time any Explosion is created, and every Explosion after that
reuses those same already-scaled Surfaces -- there's no reason to reload
and rescale the same three PNGs from disk for every single mine that
goes off.
"""

import pygame

import settings

_frames = None  # built lazily, the first time an Explosion is created


def _get_frames():
    global _frames
    if _frames is None:
        size = (settings.EXPLOSION_DISPLAY_SIZE, settings.EXPLOSION_DISPLAY_SIZE)
        _frames = []
        for path in settings.EXPLOSION_FRAME_PATHS:
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.smoothscale(image, size)
            _frames.append(image)
    return _frames


class Explosion:
    def __init__(self, center):
        """center is a WORLD-pixel (x, y) point -- the mine's own
        rect.center, so the flash appears exactly where the mine was."""
        self.frames = _get_frames()
        self.center = center
        self.frame_index = 0
        self.frame_timer = settings.EXPLOSION_FRAME_DURATION

    @property
    def is_finished(self):
        """True once every frame has had its turn -- main.py drops
        finished explosions from its list each frame, same pattern as
        expired projectiles/pickups elsewhere in this game."""
        return self.frame_index >= len(self.frames)

    def update(self, dt):
        if self.is_finished:
            return
        self.frame_timer -= dt
        while self.frame_timer <= 0 and not self.is_finished:
            self.frame_timer += settings.EXPLOSION_FRAME_DURATION
            self.frame_index += 1

    def draw(self, screen, camera_x, camera_y):
        if self.is_finished:
            return
        image = self.frames[self.frame_index]
        rect = image.get_rect(
            center=(self.center[0] - camera_x, self.center[1] - camera_y)
        )
        screen.blit(image, rect)
