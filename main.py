"""
Step 5: the room is now bigger than the window, and a camera follows the
player around so they stay centered on screen.

New idea introduced here: WORLD coordinates vs SCREEN coordinates.
  - player_rect and room_rect live in the WORLD -- e.g. the player might be
    at world position (900, 700) inside a 1600x1200 room. That position has
    nothing to do with where it's drawn on your 800x600 window.
  - camera_x/camera_y is the world position of the window's top-left corner.
  - To draw anything, we subtract the camera from its world position to get
    a SCREEN position: screen_x = world_x - camera_x. Every single thing we
    draw from now on (player, walls, enemies, items) will need this same
    conversion, which is exactly what a Camera class will do for us once we
    introduce one -- for now we do it by hand so the idea is crystal clear.

Step 6: the room is now an actual grid of tiles instead of one flat-colored
rectangle. The outermost ring of tiles is a solid wall (its own checkerboard
color); everything inside is floor (a different checkerboard). The player
can now only move within the floor tiles -- walls are solid.
"""

import pygame

import settings


def main():
    pygame.init()
    pygame.display.set_caption("Dark Rooms")
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # The room itself, in WORLD coordinates -- always starts at (0, 0).
    room_rect = pygame.Rect(0, 0, settings.ROOM_WIDTH, settings.ROOM_HEIGHT)

    # The playable floor area is the room minus its 1-tile-thick wall
    # border on every side. The player is only allowed inside this rect --
    # this is what makes the walls solid instead of just decorative.
    t = settings.TILE_SIZE
    floor_area_rect = room_rect.inflate(-2 * t, -2 * t)

    # The player's position is now a position INSIDE the room (world
    # coordinates), not a position on the screen. We start in the middle
    # of the room rather than the middle of the window.
    player_rect = pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE)
    player_rect.center = room_rect.center

    dt = 0  # time (seconds) since the last frame; updated at the end of each loop
    running = True
    while running:
        # 1. Handle input/events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Update game state
        # pygame.key.get_pressed() returns the CURRENT state of every key,
        # so movement keeps happening for as long as a key is held down
        # (unlike pygame.KEYDOWN events, which only fire once per press).
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1

        player_rect.x += dx * settings.PLAYER_SPEED * dt
        player_rect.y += dy * settings.PLAYER_SPEED * dt

        # clamp_ip() pushes player_rect back inside floor_area_rect if it's
        # poking out on any side -- now the player is stopped by the actual
        # wall tiles, not just an invisible line at the room's outer edge.
        player_rect.clamp_ip(floor_area_rect)

        # Point the camera at the player: camera_x/camera_y is the world
        # position that should appear at the window's top-left corner, so
        # we offset by half the screen size to keep the player centered.
        camera_x = player_rect.centerx - settings.SCREEN_WIDTH // 2
        camera_y = player_rect.centery - settings.SCREEN_HEIGHT // 2

        # Don't let the camera scroll past the room's own edges -- otherwise
        # we'd see empty void beyond the room whenever the player gets close
        # to a wall.
        camera_x = max(0, min(camera_x, settings.ROOM_WIDTH - settings.SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, settings.ROOM_HEIGHT - settings.SCREEN_HEIGHT))

        # 3. Draw everything
        # Everything below is drawn at (world_position - camera), which is
        # what actually converts world coordinates into screen coordinates.
        screen.fill(settings.BG_COLOR)

        # Only draw the tiles that could actually be visible on screen right
        # now, instead of every tile in the whole room -- this is a cheap
        # habit to build early, since a real dungeon room could have far more
        # tiles than fit on screen at once.
        first_tx = camera_x // t
        first_ty = camera_y // t
        last_tx = (camera_x + settings.SCREEN_WIDTH) // t + 1
        last_ty = (camera_y + settings.SCREEN_HEIGHT) // t + 1

        for ty in range(first_ty, last_ty):
            for tx in range(first_tx, last_tx):
                is_wall = (
                    tx == 0 or ty == 0
                    or tx == settings.ROOM_TILES_WIDE - 1
                    or ty == settings.ROOM_TILES_TALL - 1
                )
                # Alternating tile shade based on tile coordinates -- this is
                # what creates the checkerboard look.
                checker = (tx + ty) % 2 == 0
                if is_wall:
                    color = settings.WALL_COLOR_A if checker else settings.WALL_COLOR_B
                else:
                    color = settings.FLOOR_COLOR_A if checker else settings.FLOOR_COLOR_B

                tile_screen_rect = pygame.Rect(
                    tx * t - camera_x, ty * t - camera_y, t, t
                )
                pygame.draw.rect(screen, color, tile_screen_rect)

        player_screen_rect = player_rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, settings.PLAYER_COLOR, player_screen_rect)

        pygame.display.flip()

        # 4. Wait so we run at a steady FPS, and remember how long that frame
        #    actually took (dt = "delta time", in seconds) for next frame's movement math.
        dt = clock.tick(settings.FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()