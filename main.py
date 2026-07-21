"""
Step 7: main.py is now just the game loop -- it creates a Room and a
Player, and each frame it: reads input, tells the player to move, points
the camera at the player, then tells the room and the player to draw
themselves. It no longer contains the movement math or tile-drawing
logic itself; that moved to player.py and room.py.
"""

import pygame

import settings
from player import Player
from room import Room


def main():
    pygame.init()
    pygame.display.set_caption("Dark Rooms")
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    room = Room()
    player = Player(center=room.rect.center)

    dt = 0  # time (seconds) since the last frame; updated at the end of each loop
    running = True
    while running:
        # 1. Handle input/events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Update game state
        keys = pygame.key.get_pressed()
        player.handle_movement(dt, keys, room.floor_area_rect)

        # Point the camera at the player, then keep it from scrolling past
        # the room's own edges.
        camera_x = player.rect.centerx - settings.SCREEN_WIDTH // 2
        camera_y = player.rect.centery - settings.SCREEN_HEIGHT // 2
        camera_x = max(0, min(camera_x, settings.ROOM_WIDTH - settings.SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, settings.ROOM_HEIGHT - settings.SCREEN_HEIGHT))

        # 3. Draw everything
        screen.fill(settings.BG_COLOR)
        room.draw(screen, camera_x, camera_y)
        player.draw(screen, camera_x, camera_y)
        pygame.display.flip()

        # 4. Wait so we run at a steady FPS, and remember how long that frame
        #    actually took (dt), for next frame's movement math.
        dt = clock.tick(settings.FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()