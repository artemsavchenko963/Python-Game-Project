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

Step 11: left-click fires a projectile in the aimed direction. Active
projectiles live in one plain list here in main.py -- there's no need for
a whole class to own "the list of all bullets" yet, a list is enough.

Step 12: holding LMB down now fires repeatedly, once every
settings.FIRE_INTERVAL seconds, instead of once per click. We switched
from reacting to a MOUSEBUTTONDOWN event to checking
pygame.mouse.get_pressed() every frame, gated by Player's cooldown timer.

Step 13: the first enemy -- a stationary square with health, sitting in
one specific room. It doesn't move, and nothing can hurt it yet; this
step is only about having an Enemy object that exists and draws itself.

Step 14: projectiles now check for a hit against the current room's
enemies FIRST, before checking walls/room-exit. A projectile that hits an
enemy is removed either way (whether or not that hit kills the enemy) --
it shouldn't also get to fly on and separately hit a wall the same frame.
"""

import pygame

import settings
from player import Player
from room import Room
from projectile import Projectile
from enemy import Enemy


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

    # Drop a single stationary enemy into one of the middle rooms, offset
    # a bit from the room's exact center (which sits right on the doorway's
    # path) so it's clearly visible off to one side as you walk in.
    enemy_room = rooms[len(rooms) // 2]
    enemy_room.enemies.append(
        Enemy(center=(enemy_room.rect.centerx, enemy_room.rect.centery - 150))
    )

    player = Player(center=rooms[current_index].rect.center)
    projectiles = []

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

        # Fire while LMB is held, at most once every FIRE_INTERVAL seconds.
        # get_pressed() checks the CURRENT held state every frame (like
        # get_pressed() for keys), so this is what makes holding the
        # button fire repeatedly instead of just once.
        player.tick_cooldown(dt)
        mouse_buttons = pygame.mouse.get_pressed()
        left_button_held = mouse_buttons[0]
        if left_button_held and player.can_fire():
            projectiles.append(Projectile(player.rect.center, player.aim_dir))
            player.reset_fire_cooldown()

        # Move every projectile, then check what it hit. Looping over
        # projectiles[:] (a copy of the list) is what makes it safe to
        # remove items from the real `projectiles` list while we're in the
        # middle of iterating it.
        for projectile in projectiles[:]:
            projectile.update(dt)

            # Check enemies first -- a projectile that hits one is used up
            # right there, regardless of whether that hit also killed it.
            hit_enemy = None
            for enemy in current_room.enemies:
                if projectile.get_rect().colliderect(enemy.rect):
                    hit_enemy = enemy
                    break

            if hit_enemy is not None:
                if hit_enemy.take_damage(settings.PROJECTILE_DAMAGE):
                    current_room.enemies.remove(hit_enemy)
                projectiles.remove(projectile)
                continue

            hit_wall = any(
                projectile.get_rect().colliderect(wall_rect)
                for wall_rect in current_room.wall_rects
            )
            left_room = not current_room.rect.collidepoint(projectile.pos)
            if hit_wall or left_room:
                projectiles.remove(projectile)

        # 3. Draw everything
        screen.fill(settings.BG_COLOR)
        current_room.draw(screen, camera_x, camera_y)
        for enemy in current_room.enemies:
            enemy.draw(screen, camera_x, camera_y)
        player.draw(screen, camera_x, camera_y)
        for projectile in projectiles:
            projectile.draw(screen, camera_x, camera_y)
        pygame.display.flip()

        # 4. Wait so we run at a steady FPS, and remember how long that frame
        #    actually took (dt), for next frame's movement math.
        dt = clock.tick(settings.FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()