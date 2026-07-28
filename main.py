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

Step 12: holding LMB down now fires repeatedly, at a fixed interval,
instead of once per click. We switched from reacting to a
MOUSEBUTTONDOWN event to checking pygame.mouse.get_pressed() every
frame, gated by Player's cooldown timer.

Step 13: the first enemy -- a stationary square with health, sitting in
one specific room. It doesn't move, and nothing can hurt it yet; this
step is only about having an Enemy object that exists and draws itself.

Step 14: projectiles now check for a hit against the current room's
enemies FIRST, before checking walls/room-exit. A projectile that hits an
enemy is removed either way (whether or not that hit kills the enemy) --
it shouldn't also get to fly on and separately hit a wall the same frame.

Step 15: enemies now chase the player. Note there's still no collision
between the player and an enemy -- touching one won't do anything (or
push you back) yet. That's the health system step, coming up soon.

Step 16: the player now has health, and touching an enemy damages them --
gated by a brief invulnerability window (the player flashes white) so
standing inside an enemy doesn't drain the whole health bar in one
second. There's no health BAR drawn yet and no game-over screen yet --
health can silently hit 0 for now. Both are coming up next.

Step 17: an on-screen health bar, via hud.py. Drawn last, after
everything in the world, so it always sits on top of the room/player/etc.

Step 18: dying now actually means something. All the gameplay UPDATE
logic (movement, chasing, damage, aiming, shooting, projectiles) is now
wrapped in `if not game_over:` -- once health hits 0, the world freezes
in place and a "YOU DIED" screen appears. Pressing R rebuilds a fresh
game from scratch. Drawing is NOT wrapped, so the frozen world stays
visible underneath the game-over overlay instead of vanishing.

Step 19: the player now carries two weapons (Pistol, SMG) with different
damage/fire-rate/projectile-speed, switchable with the 1/2 keys.
Projectiles and fire_cooldown both now pull their numbers from
player.equipped_weapon instead of fixed settings constants.

Step 20: the player now starts with ONLY the Pistol. The SMG has to be
found as a WeaponPickup lying in a room -- walking over it calls
player.add_weapon(), which also auto-equips it.

Step 21: the room chain is gone. There's now a single, big map loaded
from a Tiled .tmx file (room.py handles the loading). No more
current_index, no more door-crossing checks -- the player and enemy just
exist somewhere on that one map, and the camera clamps to the whole
map's pixel size instead of one room's. Collision against the map is
OFF for now (Room.wall_rects is empty) -- that's a deliberate choice
while the map itself is still being tested, not a bug.

Step 22: camera zoom. Everything now gets drawn onto a small internal
surface (game_surface) instead of the real window -- that internal
surface is settings.ZOOM times smaller than the window in each
dimension. At the very end of the frame, that small surface gets
stretched up to fill the actual window. The net effect: a smaller slice
of the map fills the same window space, so the camera feels closer to
the player. The window size itself (settings.SCREEN_WIDTH/HEIGHT)
hasn't changed -- only how much of the WORLD fits inside it.

Step 23: wall collision is live. room.py now builds real wall_rects from
any tile tagged "solid" in the Tiled tileset -- nothing changed here in
main.py, since Player.handle_movement/Enemy.update/the projectile-vs-
wall check already used room.wall_rects, they just had nothing in it
before.

Step 24: player and enemy movement speed are both three times slower
(see PLAYER_SPEED/ENEMY_SPEED in settings.py) -- nothing to change here,
main.py just reads whatever speed settings.py provides.

Step 25: the game launches full screen, and there's a pause button in
the top-right corner. Pausing works exactly like the game-over freeze --
the update block below is skipped while paused, so the world stops in
place -- but with its own overlay and just a "Leave" button for now
(closes the game). The pause button/overlay are drawn directly on the
real window, AFTER the zoomed game_surface is stretched onto it, so they
stay a fixed, crisp size regardless of ZOOM.
"""

import pygame

import settings
from player import Player
from room import Room
from projectile import Projectile
from enemy import Enemy
from weapon import Weapon
from pickup import WeaponPickup
import hud


def create_game_state():
    """Build everything a fresh run needs: the map, one enemy, the
    player, and an empty projectile list. Called once at startup and
    again every time the player restarts after dying."""
    room = Room()

    # Enemy spawns wherever the map's own "enemy" object says to, instead
    # of a hardcoded room/offset. Falls back to the map's center if the
    # map somehow has no enemy spawn object, so this never crashes.
    enemy_spawn = room.enemy_spawn or room.rect.center
    room.enemies.append(Enemy(center=enemy_spawn))

    # Player spawns at the map's "spawnpoint" object, same fallback idea.
    player_spawn = room.player_spawn or room.rect.center
    player = Player(center=player_spawn)

    # An SMG pickup near the player's start, so there's still something
    # to grab early on -- offset to the side so it's not sitting exactly
    # on top of the spawn point.
    smg_weapon = Weapon("SMG", settings.SMG_DAMAGE, settings.SMG_FIRE_INTERVAL, settings.SMG_PROJECTILE_SPEED)
    pickup_center = (player_spawn[0] + 150, player_spawn[1])
    room.items.append(WeaponPickup(center=pickup_center, weapon=smg_weapon))

    projectiles = []
    return room, player, projectiles


def main():
    pygame.init()
    pygame.display.set_caption("Dark Rooms")

    # Full screen now, at whatever resolution the monitor actually is --
    # so settings.SCREEN_WIDTH/HEIGHT get overwritten here with the real
    # size instead of the old fixed 1440x900 fallback.
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT = screen.get_size()

    clock = pygame.time.Clock()

    # The world is drawn onto this smaller surface, then scaled up to
    # fill the real window each frame -- that's the whole zoom effect
    # (see the step 22 note in the module docstring above).
    view_width = settings.SCREEN_WIDTH // settings.ZOOM
    view_height = settings.SCREEN_HEIGHT // settings.ZOOM
    game_surface = pygame.Surface((view_width, view_height))

    room, player, projectiles = create_game_state()
    game_over = False
    paused = False

    dt = 0  # time (seconds) since the last frame; updated at the end of each loop
    running = True
    while running:
        # 1. Handle input/events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_r:
                room, player, projectiles = create_game_state()
                game_over = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not paused and hud.get_pause_button_rect(screen).collidepoint(event.pos):
                    paused = True
                elif paused and hud.get_leave_button_rect(screen).collidepoint(event.pos):
                    running = False

        # 2. Update game state -- entirely skipped once game_over is True
        # OR the game is paused, which is what makes the world freeze in
        # place instead of continuing to move behind the overlay.
        if not game_over and not paused:
            keys = pygame.key.get_pressed()
            player.handle_movement(dt, keys, room.wall_rects)
            player.handle_weapon_switch(keys)

            # Chase behavior: every enemy on the map moves toward the
            # player each frame, colliding with the map's walls just like
            # the player does.
            for enemy in room.enemies:
                enemy.update(dt, player, room.wall_rects)

            # Touching an enemy damages the player, unless still
            # invulnerable from a recent hit. take_damage() returns True
            # once health hits 0 -- that's what ends the run.
            player.tick_invulnerability(dt)
            for enemy in room.enemies:
                if player.rect.colliderect(enemy.rect):
                    if player.take_damage(settings.ENEMY_TOUCH_DAMAGE):
                        game_over = True

            # Walking over a weapon pickup collects it. Looping over
            # room.items[:] (a copy) for the same reason as the
            # projectile list -- we remove from the real list mid-loop.
            for item in room.items[:]:
                if player.rect.colliderect(item.rect):
                    player.add_weapon(item.weapon)
                    room.items.remove(item)

            # Point the camera at the player, then keep it from scrolling
            # past the MAP's own edges (room.rect is now the whole map).
            # Uses view_width/view_height (the zoomed-in internal surface
            # size), not the real window size, since that's how much
            # world is actually visible at once.
            camera_x = player.rect.centerx - view_width // 2
            camera_y = player.rect.centery - view_height // 2
            camera_x = max(0, min(camera_x, room.rect.width - view_width))
            camera_y = max(0, min(camera_y, room.rect.height - view_height))

            player.handle_aim(camera_x, camera_y)

            # Fire while LMB is held, at most once every
            # equipped_weapon.fire_interval seconds.
            player.tick_cooldown(dt)
            mouse_buttons = pygame.mouse.get_pressed()
            left_button_held = mouse_buttons[0]
            if left_button_held and player.can_fire():
                weapon = player.equipped_weapon
                projectiles.append(
                    Projectile(player.rect.center, player.aim_dir, weapon.projectile_speed, weapon.damage)
                )
                player.reset_fire_cooldown()

            # Move every projectile, then check what it hit. Looping over
            # projectiles[:] (a copy of the list) is what makes it safe to
            # remove items from the real `projectiles` list while we're in
            # the middle of iterating it.
            for projectile in projectiles[:]:
                projectile.update(dt)

                hit_enemy = None
                for enemy in room.enemies:
                    if projectile.get_rect().colliderect(enemy.rect):
                        hit_enemy = enemy
                        break

                if hit_enemy is not None:
                    if hit_enemy.take_damage(projectile.damage):
                        room.enemies.remove(hit_enemy)
                    projectiles.remove(projectile)
                    continue

                hit_wall = any(
                    projectile.get_rect().colliderect(wall_rect)
                    for wall_rect in room.wall_rects
                )
                left_map = not room.rect.collidepoint(projectile.pos)
                if hit_wall or left_map:
                    projectiles.remove(projectile)

        # 3. Draw everything -- always runs, game over or not, so the
        # frozen world stays visible underneath the game-over overlay.
        # Everything draws onto game_surface (the smaller, zoomed-in
        # surface), never directly onto the real window.
        game_surface.fill(settings.BG_COLOR)
        room.draw(game_surface, camera_x, camera_y)
        for item in room.items:
            item.draw(game_surface, camera_x, camera_y)
        for enemy in room.enemies:
            enemy.draw(game_surface, camera_x, camera_y)
        player.draw(game_surface, camera_x, camera_y)
        for projectile in projectiles:
            projectile.draw(game_surface, camera_x, camera_y)

        hud.draw_health_bar(game_surface, player)
        hud.draw_weapon_label(game_surface, player)
        if game_over:
            hud.draw_game_over(game_surface)

        # Stretch the finished frame up to fill the real window -- this
        # one line is what actually makes everything look "zoomed in".
        pygame.transform.scale(game_surface, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), screen)

        # Pause button/overlay draw directly on the real window, AFTER
        # the zoomed world is stretched onto it -- so they sit on top of
        # everything, and stay a fixed size no matter what ZOOM is.
        hud.draw_pause_button(screen)
        if paused:
            hud.draw_pause_overlay(screen)

        pygame.display.flip()

        # 4. Wait so we run at a steady FPS, and remember how long that frame
        #    actually took (dt), for next frame's movement math.
        dt = clock.tick(settings.FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()