"""
VHS / old-CRT-TV look: a fullscreen overlay drawn on top of the finished
world frame (main.py draws it right after the zoomed game_surface is
stretched onto the real window, and BEFORE the crisp screen-space HUD, so
the health bar / buttons / shop stay readable while the world gets the
grainy-tape treatment).

Everything expensive is built ONCE in __init__ (scanlines, vignette,
a few grain frames, the tracking band) -- per frame it's only a handful
of blits, so it costs a couple of milliseconds, not a per-pixel loop.

Layers, back to front:
  1. glitch  -- now and then a few horizontal slices of the picture get
                shoved sideways for a split second (tape tracking tear)
  2. grain   -- random static, a different pre-built frame every tick
  3. scanlines -- thin dark horizontal lines
  4. tracking band -- a faint bright bar slowly rolling down the screen
  5. flicker -- the whole picture dips a touch darker at random
  6. vignette -- dark rounded corners, like a curved tube

Tunable (or switchable off, V key in-game) via settings.VHS_*.
"""

import math
import os
import random

import pygame

import settings


def _build_scanlines(width, height):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    color = (0, 0, 0, settings.VHS_SCANLINE_ALPHA)
    spacing = settings.VHS_SCANLINE_SPACING
    thickness = settings.VHS_SCANLINE_THICKNESS
    for y in range(0, height, spacing):
        surface.fill(color, (0, y, width, thickness))
    return surface


def _build_vignette(width, height):
    """Dark corners. Computed on a tiny grid (cheap per-pixel loop) and
    smoothscaled up to full size -- same trick the old fog of war used."""
    small_w, small_h = 96, 54
    small = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
    cx, cy = (small_w - 1) / 2, (small_h - 1) / 2
    max_alpha = settings.VHS_VIGNETTE_STRENGTH
    for y in range(small_h):
        for x in range(small_w):
            # 0 at the center, 1 at the edge midpoints, >1 in the corners
            nx = (x - cx) / cx
            ny = (y - cy) / cy
            distance = math.sqrt(nx * nx + ny * ny) / math.sqrt(2)
            falloff = max(0.0, (distance - 0.45) / 0.55)
            alpha = int(max_alpha * min(1.0, falloff) ** 2)
            small.set_at((x, y), (0, 0, 0, alpha))
    return pygame.transform.smoothscale(small, (width, height))


def _build_grain_frames(width, height):
    """A few full-size static frames. Random bytes -> gray RGBA at 1/GRAIN_SCALE
    resolution (so each speck is a few pixels wide, like real tape noise),
    then scaled up. os.urandom + bytes.translate keeps this fast with no
    per-pixel Python loop."""
    scale = settings.VHS_GRAIN_SCALE
    small_w, small_h = max(1, width // scale), max(1, height // scale)
    count = small_w * small_h
    max_alpha = settings.VHS_GRAIN_MAX_ALPHA
    alpha_table = bytes(int(i * max_alpha / 255) for i in range(256))

    frames = []
    for _ in range(settings.VHS_GRAIN_FRAMES):
        gray = os.urandom(count)
        buffer = bytearray(count * 4)
        buffer[0::4] = gray
        buffer[1::4] = gray
        buffer[2::4] = gray
        buffer[3::4] = os.urandom(count).translate(alpha_table)
        small = pygame.image.frombuffer(bytes(buffer), (small_w, small_h), "RGBA").convert_alpha()
        frames.append(pygame.transform.scale(small, (width, height)))
    return frames


def _build_band(width):
    """A soft horizontal bar: transparent at top/bottom edges, brightest
    in the middle."""
    height = settings.VHS_BAND_HEIGHT
    band = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        t = 1 - abs((y / (height - 1)) * 2 - 1)  # 0 at edges, 1 in the middle
        alpha = int(settings.VHS_BAND_ALPHA * t)
        band.fill((255, 255, 255, alpha), (0, y, width, 1))
    return band


class VHSOverlay:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.scanlines = _build_scanlines(width, height)
        self.vignette = _build_vignette(width, height)
        self.grain_frames = _build_grain_frames(width, height)
        self.band = _build_band(width)
        self.flicker = pygame.Surface((width, height))
        self.flicker.fill((0, 0, 0))

        self.time = 0.0
        self.band_y = -settings.VHS_BAND_HEIGHT
        self.grain_index = 0
        self.flicker_alpha = 0

        self.glitch_timer = random.uniform(
            settings.VHS_GLITCH_MIN_INTERVAL, settings.VHS_GLITCH_MAX_INTERVAL
        )
        self.glitch_remaining = 0.0
        self.glitch_slices = []  # [(y, height, x_offset), ...] while a glitch is active

    def update(self, dt):
        self.time += dt

        self.band_y += settings.VHS_BAND_SPEED * dt
        if self.band_y > self.height:
            self.band_y = -settings.VHS_BAND_HEIGHT

        self.grain_index = random.randrange(len(self.grain_frames))
        self.flicker_alpha = random.randint(0, settings.VHS_FLICKER_MAX_ALPHA)

        if self.glitch_remaining > 0:
            self.glitch_remaining -= dt
            if self.glitch_remaining <= 0:
                self.glitch_slices = []
                self.glitch_timer = random.uniform(
                    settings.VHS_GLITCH_MIN_INTERVAL, settings.VHS_GLITCH_MAX_INTERVAL
                )
        else:
            self.glitch_timer -= dt
            if self.glitch_timer <= 0:
                self.glitch_remaining = settings.VHS_GLITCH_DURATION
                self.glitch_slices = []
                for _ in range(settings.VHS_GLITCH_SLICES):
                    slice_height = random.randint(8, settings.VHS_GLITCH_MAX_SLICE_HEIGHT)
                    y = random.randint(0, max(0, self.height - slice_height))
                    offset = random.choice((-1, 1)) * random.randint(8, settings.VHS_GLITCH_MAX_OFFSET)
                    self.glitch_slices.append((y, slice_height, offset))

    def draw(self, screen):
        for y, slice_height, offset in self.glitch_slices:
            strip = screen.subsurface((0, y, self.width, slice_height)).copy()
            screen.blit(strip, (offset, y))

        screen.blit(self.grain_frames[self.grain_index], (0, 0))
        screen.blit(self.scanlines, (0, 0))
        screen.blit(self.band, (0, int(self.band_y)))

        self.flicker.set_alpha(self.flicker_alpha)
        screen.blit(self.flicker, (0, 0))

        screen.blit(self.vignette, (0, 0))
