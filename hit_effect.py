"""
Step 43 gave this a procedural glow because the user's original ef1.gif
was a noisy, unusable single frame. Step 44 replaces that with the real
thing: three actual frames (ef1/ef2/ef3.png, a spark growing into a
burst), cycled once and gone -- same overall shape as explosion.py.

Shown for an instant wherever a bullet actually hits something (an
enemy, or the player) -- purely a visual "impact" cue, no gameplay
effect of its own.
"""

import pygame

import settings


_frames = None  # loaded, cleaned up, and scaled once -- shared by every HitEffect


def _remove_checker_background(surface):
    """These PNGs are fully opaque (no real alpha channel) -- the
    background is a two-tone mid-gray checkerboard baked into the pixels
    instead. Unlike player.py/mine.py/projectile.py's single "bright
    enough" threshold, this checker is fairly dark (~102 and ~139
    brightness), so instead this checks closeness to those two specific
    checker tones (settings.HIT_EFFECT_CHECKER_COLORS) rather than a
    one-sided brightness cutoff -- the spark art itself is either much
    brighter (the bluish-white core) or, where it blends toward the
    edges, has actual blue color tint rather than being flat gray, so it
    never gets caught by this."""
    surface = surface.convert_alpha()
    width, height = surface.get_size()
    surface.lock()
    for x in range(width):
        for y in range(height):
            r, g, b, a = surface.get_at((x, y))
            brightness = (r + g + b) / 3
            is_grayish = abs(r - g) <= 8 and abs(g - b) <= 8 and abs(r - b) <= 8
            is_checker_toned = any(
                abs(brightness - checker) < settings.HIT_EFFECT_CHECKER_TOLERANCE
                for checker in settings.HIT_EFFECT_CHECKER_COLORS
            )
            if is_grayish and is_checker_toned:
                surface.set_at((x, y), (r, g, b, 0))
    surface.unlock()
    return surface


def _load_frame(path):
    image = pygame.image.load(path)
    image = _remove_checker_background(image)

    bounding_rect = image.get_bounding_rect()
    if bounding_rect.width > 0 and bounding_rect.height > 0:
        image = image.subsurface(bounding_rect).copy()

    size = (settings.HIT_EFFECT_DISPLAY_SIZE, settings.HIT_EFFECT_DISPLAY_SIZE)
    return pygame.transform.smoothscale(image, size)


def _get_frames():
    global _frames
    if _frames is None:
        _frames = [_load_frame(path) for path in settings.HIT_EFFECT_FRAME_PATHS]
    return _frames


class HitEffect:
    def __init__(self, center):
        self.center = center
        self.frames = _get_frames()
        self.frame_index = 0
        self.frame_timer = settings.HIT_EFFECT_FRAME_DURATION

    @property
    def is_finished(self):
        return self.frame_index >= len(self.frames)

    def update(self, dt):
        if self.is_finished:
            return
        self.frame_timer -= dt
        while self.frame_timer <= 0 and not self.is_finished:
            self.frame_timer += settings.HIT_EFFECT_FRAME_DURATION
            self.frame_index += 1

    def draw(self, screen, camera_x, camera_y):
        if self.is_finished:
            return
        image = self.frames[self.frame_index]
        rect = image.get_rect(center=(self.center[0] - camera_x, self.center[1] - camera_y))
        screen.blit(image, rect)
