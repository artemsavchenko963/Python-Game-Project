"""
Room: owns the tile grid for one room -- where the walls are, where the
floor is, which walls have a doorway gap in them, and how to draw only
the tiles currently visible on screen.
"""

import pygame

import settings


class Room:
    def __init__(self, doors=None):
        self.rect = pygame.Rect(0, 0, settings.ROOM_WIDTH, settings.ROOM_HEIGHT)

        # Which sides have a doorway gap in the wall, e.g. {"east", "west"}.
        self.doors = doors or set()

        # The doorway gap is always centered on whichever wall it's on, and
        # is the same few tiles tall on every room, so two connected rooms'
        # doorways always line up with each other.
        span = settings.DOOR_SPAN_TILES
        self._door_row_start = settings.ROOM_TILES_TALL // 2 - span // 2

        # Precompute which tiles are solid walls (used for both drawing and
        # collision) now that a doorway can leave a gap in the wall ring.
        self.wall_rects = self._build_wall_rects()

    def _is_door_gap(self, tx, ty):
        span = settings.DOOR_SPAN_TILES
        row_ok = self._door_row_start <= ty < self._door_row_start + span
        if not row_ok:
            return False
        if "east" in self.doors and tx == settings.ROOM_TILES_WIDE - 1:
            return True
        if "west" in self.doors and tx == 0:
            return True
        return False

    def is_wall_tile(self, tx, ty):
        on_border = (
            tx == 0 or ty == 0
            or tx == settings.ROOM_TILES_WIDE - 1
            or ty == settings.ROOM_TILES_TALL - 1
        )
        if not on_border:
            return False
        return not self._is_door_gap(tx, ty)

    def _build_wall_rects(self):
        """One Rect per solid wall tile. Doorway gap tiles are skipped on
        purpose -- that's what makes them passable instead of solid."""
        t = settings.TILE_SIZE
        rects = []
        for ty in range(settings.ROOM_TILES_TALL):
            for tx in range(settings.ROOM_TILES_WIDE):
                if self.is_wall_tile(tx, ty):
                    rects.append(pygame.Rect(tx * t, ty * t, t, t))
        return rects

    def draw(self, screen, camera_x, camera_y):
        t = settings.TILE_SIZE

        first_tx = camera_x // t
        first_ty = camera_y // t
        last_tx = (camera_x + settings.SCREEN_WIDTH) // t + 1
        last_ty = (camera_y + settings.SCREEN_HEIGHT) // t + 1

        for ty in range(first_ty, last_ty):
            for tx in range(first_tx, last_tx):
                checker = (tx + ty) % 2 == 0
                if self.is_wall_tile(tx, ty):
                    color = settings.WALL_COLOR_A if checker else settings.WALL_COLOR_B
                else:
                    color = settings.FLOOR_COLOR_A if checker else settings.FLOOR_COLOR_B

                tile_rect = pygame.Rect(tx * t - camera_x, ty * t - camera_y, t, t)
                pygame.draw.rect(screen, color, tile_rect)