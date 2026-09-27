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


# Step 40: the mine icon, loaded/cleaned/scaled once and shared by every
# Mine -- there can be hundreds of these on a map, no reason to reload
# and reprocess the same image that many times.
_image = None


def _remove_checker_background(surface):
    """mine.jpg is a plain JPEG, so it can't store real transparency --
    the background is a light gray/white checkerboard baked into the
    pixels instead. Same approach as player.py's version of this: any
    pixel that's both close to gray (r, g, and b all near each other)
    and bright enough to be checker rather than artwork gets turned
    fully transparent. The mine's own colors (dark metal, red core) are
    never close to gray/bright enough to get caught by this."""
    surface = surface.convert_alpha()
    width, height = surface.get_size()
    surface.lock()
    for x in range(width):
        for y in range(height):
            r, g, b, a = surface.get_at((x, y))
            brightness = (r + g + b) / 3
            is_grayish = abs(r - g) <= 8 and abs(g - b) <= 8 and abs(r - b) <= 8
            if is_grayish and brightness >= settings.MINE_CHECKER_BRIGHTNESS_THRESHOLD:
                surface.set_at((x, y), (r, g, b, 0))
    surface.unlock()
    return surface


def _get_image():
    global _image
    if _image is None:
        image = pygame.image.load(settings.MINE_IMAGE_PATH)
        image = _remove_checker_background(image)
        size = (settings.MINE_DISPLAY_SIZE, settings.MINE_DISPLAY_SIZE)
        _image = pygame.transform.smoothscale(image, size)
    return _image


class Mine:
    def __init__(self, center):
        self.rect = pygame.Rect(0, 0, settings.MINE_SIZE, settings.MINE_SIZE)
        self.rect.center = center

        # Counts down to 0 every frame (main.py calls update(dt)) --
        # only drawn while this is above 0. Starts at 0 so a fresh mine
        # is invisible until a scan actually finds it.
        self.revealed_timer = 0.0

        # Loaded lazily (not at import time) since it needs pygame's
        # display already initialized -- by the time any Mine actually
        # gets created (create_game_state, after main() sets the video
        # mode), that's always already true.
        self.image = _get_image()

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
        screen_center = (self.rect.centerx - camera_x, self.rect.centery - camera_y)
        image_rect = self.image.get_rect(center=screen_center)
        screen.blit(self.image, image_rect)