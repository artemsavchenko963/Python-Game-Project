"""
Step 9: instead of two hand-placed rooms, generate a whole chain of them
in a loop. Every room (except the first) gets a west door back to the
previous room; every room (except the last) gets an east door forward to
the next one. Still a straight line, not random yet -- that's a later
step -- but it's now GENERATED rather than typed out one room at a time.

Step 10: the player now aims toward the mouse cursor. handle_aim() needs
to know where the camera is (it converts the player's world position to
a screen position to compare against the mouse, which is always in
screen coordinates), so it has to run AFTER the camera is computed.
"""

import pygame

import settings
from player import Player
from room import Room


def generate_room_chain(num_rooms):
    """Build a simple in-a-row sequence of connected rooms."""
    rooms = []
    for i in range(num_rooms):
        doors = set()
        if i > 0:
            doors.add("west")           # connects back to the previous room
        if i < num_rooms - 1:
            doors.add("east")           # connects forward to the next room
        rooms.append(Room(doors=doors))
    return rooms


def main():
    pygame.init()
    pygame.display.set_caption("Dark Rooms")
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    rooms = generate_room_chain(settings.NUM_ROOMS)
    current_index = 0

    player = Player(center=rooms[current_index].rect.center)

    dt = 0  # time (seconds) since the last frame; updated at the end of each loop
    running = True
    while running:
        # 1. Handle input/events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Update game state
        current_room = rooms[current_index]
        keys = pygame.key.get_pressed()
        player.handle_movement(dt, keys, current_room.wall_rects)

        # Once the player has walked fully past a doorway's outer edge,
        # move to the next/previous room in the chain and place them just
        # inside its matching doorway on the opposite side.
        if "east" in current_room.doors and player.rect.left > current_room.rect.right:
            current_index += 1
            player.rect.left = settings.TILE_SIZE + settings.DOOR_ENTRY_MARGIN
        elif "west" in current_room.doors and player.rect.right < current_room.rect.left:
            current_index -= 1
            new_room = rooms[current_index]
            player.rect.right = new_room.rect.right - settings.TILE_SIZE - settings.DOOR_ENTRY_MARGIN

        current_room = rooms[current_index]

        # Point the camera at the player, then keep it from scrolling past
        # the CURRENT room's own edges.
        camera_x = player.rect.centerx - settings.SCREEN_WIDTH // 2
        camera_y = player.rect.centery - settings.SCREEN_HEIGHT // 2
        camera_x = max(0, min(camera_x, settings.ROOM_WIDTH - settings.SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, settings.ROOM_HEIGHT - settings.SCREEN_HEIGHT))

        player.handle_aim(camera_x, camera_y)

        # 3. Draw everything
        screen.fill(settings.BG_COLOR)
        current_room.draw(screen, camera_x, camera_y)
        player.draw(screen, camera_x, camera_y)
        pygame.display.flip()

        # 4. Wait so we run at a steady FPS, and remember how long that frame
        #    actually took (dt), for next frame's movement math.
        dt = clock.tick(settings.FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()