"""
Projectile: a single bullet fired by the player OR a guardian. Travels in
a straight line at a fixed speed until main.py decides it hit something
(or a wall, or left the map), and removes it from whichever list
(projectiles / enemy_projectiles) it's currently sitting in.

Position is stored as a pygame.Vector2 (which allows fractional/float
values) rather than a pygame.Rect (which only stores whole pixels) --
that matters here because a slow-ish, precise-feeling bullet needs
smooth sub-pixel movement, not the same integer rounding we accepted for
the player square.

Speed and damage are passed in rather than read from settings directly
(step 19) -- different weapons fire projectiles with different stats, so
the projectile just carries whatever numbers it was given, with no idea
which weapon made it.

Step 43: drawn as a rotated bullet.png sprite instead of a plain circle.
A bullet's direction never changes after it's fired, so the rotated
image is built ONCE per Projectile (in __init__), not re-rotated every
frame -- there's no reason to redo that work 60 times a second for
something that never changes.
"""

import math

import pygame

import settings


_base_image = None  # the artwork, cleaned up and scaled -- built once, shared by every bullet


def _remove_checker_background(surface):
    """bullet.png is fully opaque (no real alpha channel) -- its
    background is a light gray/white checkerboard baked into the pixels
    instead of true transparency. Same approach as player.py/mine.py:
    any pixel that's both close to gray and bright enough to be checker
    rather than artwork gets turned fully transparent."""
    surface = surface.convert_alpha()
    width, height = surface.get_size()
    surface.lock()
    for x in range(width):
        for y in range(height):
            r, g, b, a = surface.get_at((x, y))
            brightness = (r + g + b) / 3
            is_grayish = abs(r - g) <= 8 and abs(g - b) <= 8 and abs(r - b) <= 8
            if is_grayish and brightness >= settings.PROJECTILE_CHECKER_BRIGHTNESS_THRESHOLD:
                surface.set_at((x, y), (r, g, b, 0))
    surface.unlock()
    return surface


def _get_base_image():
    global _base_image
    if _base_image is None:
        image = pygame.image.load(settings.PROJECTILE_IMAGE_PATH)
        image = _remove_checker_background(image)

        bounding_rect = image.get_bounding_rect()
        if bounding_rect.width > 0 and bounding_rect.height > 0:
            image = image.subsurface(bounding_rect).copy()

        width, height = image.get_size()
        scale = settings.PROJECTILE_SPRITE_LENGTH / width
        new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
        _base_image = pygame.transform.smoothscale(image, new_size)
    return _base_image


class Projectile:
    def __init__(self, world_pos, direction, speed, damage):
        self.pos = pygame.Vector2(world_pos)
        self.velocity = direction * speed
        self.damage = damage

        # The artwork's default pose points right (angle 0, along +x).
        # -direction.y flips for pygame's downward-positive y-axis, so
        # the sprite's nose actually ends up leading the direction of
        # travel on screen instead of mirrored.
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        self.image = pygame.transform.rotate(_get_base_image(), angle)

    def update(self, dt):
        self.pos += self.velocity * dt

    def get_rect(self):
        """A small square around the projectile's position, for collision checks --
        deliberately independent of how big the sprite is drawn."""
        r = settings.PROJECTILE_RADIUS
        return pygame.Rect(self.pos.x - r, self.pos.y - r, r * 2, r * 2)

    def draw(self, screen, camera_x, camera_y):
        screen_pos = (self.pos.x - camera_x, self.pos.y - camera_y)
        image_rect = self.image.get_rect(center=screen_pos)
        screen.blit(self.image, image_rect)
