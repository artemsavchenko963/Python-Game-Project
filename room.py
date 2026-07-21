"""
Room: owns the tile grid for one room -- where the walls are, where the
floor is, and how to draw only the tiles currently visible on screen.

Pulled out of main.py for the same reason as Player: main.py shouldn't
need to know HOW the checkerboard pattern is computed or which tiles
count as walls. It just creates a Room and calls room.draw(). This is
also the class that will grow doors, enemy lists, and item lists once we
get to multiple rooms and enemies.
"""

import pygame

import settings


class Room:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, settings.ROOM_WIDTH, settings.ROOM_HEIGHT)

        # The playable floor area is the room minus its 1-tile-thick wall
        # border on every side -- this is what the player gets clamped to.
        t = settings.TILE_SIZE
        self.floor_area_rect = self.rect.inflate(-2 * t, -2 * t)

    def is_wall_tile(self, tx, ty):
        return (
            tx == 0 or ty == 0
            or tx == settings.ROOM_TILES_WIDE - 1
            or ty == settings.ROOM_TILES_TALL - 1
        )

    def draw(self, screen, camera_x, camera_y):
        t = settings.TILE_SIZE

        # Only figure out and draw tiles that could actually be visible.
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