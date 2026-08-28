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

Step 26: each object on the map's "enemy" layer is now the CENTER of a
whole BASE, not a single enemy (room.py reads them as room.base_spawns).
For each base, create_game_state() builds one stationary, tanky
"guardian" Enemy exactly there, plus a random scattered group of 10-15
regular enemies around it (regular enemies only chase once you're within
AGGRO_RADIUS -- see enemy.py). `bases` is a list of small dicts
{"guardian": ..., "minions": [...]} used only to compute how many bases
are still standing, for the HUD counter -- a base counts as cleared once
its guardian AND every one of its minions are dead.

Step 27: guardians shoot. enemy_projectiles is a SEPARATE list from the
player's own `projectiles` -- kept apart because the collision rules are
different (an enemy projectile hits the PLAYER, never other enemies; the
player's own projectiles hit enemies, never the player). Enemy.update()
returns a new Projectile when a guardian just fired; main.py is what
actually appends it into enemy_projectiles and moves/collides it every
frame from there, the same way it already handles the player's shots.

Step 29: the "wall" layer (fence/wall tiles) is no longer flattened into
the same background image as everything else -- room.py now pre-renders
it separately (room.foreground) and main.py draws it AFTER the
player/enemies/projectiles each frame, via room.draw_foreground(). That's
what makes fence tiles visually cover the player when they're standing
"in front of" one from the camera's point of view, instead of the player
always drawing on top of every tile on the map.
"""

import random

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
    """Build everything a fresh run needs: the map, every base (a
    stationary guardian plus a scattered group of regular enemies around
    it), the player, and an empty projectile list. Called once at
    startup and again every time the player restarts after dying."""
    room = Room()

    # Step 31: this USED to fall back to a single base at the map's dead
    # center whenever room.base_spawns came back empty ("or
    # [room.rect.center]") -- meant to avoid crashing on a totally blank
    # map early on. But that silent fallback is exactly what caused
    # enemies to keep appearing after deleting every "enemy" point in
    # Tiled, or a brand new point to seemingly "spawn somewhere else" --
    # in both cases room.base_spawns was actually empty (nothing valid
    # was read from the map), so it silently substituted one base
    # sitting at the map's exact center instead of showing "0 bases."
    # Now an empty map genuinely means zero bases -- no substitute.
    base_spawns = room.base_spawns
    bases = []
    for base_center in base_spawns:
        guardian = Enemy(center=base_center, is_guardian=True)

        minion_count = random.randint(settings.BASE_MIN_ENEMIES, settings.BASE_MAX_ENEMIES)
        minions = []
        for _ in range(minion_count):
            offset_x = random.uniform(-settings.BASE_SCATTER_RADIUS, settings.BASE_SCATTER_RADIUS)
            offset_y = random.uniform(-settings.BASE_SCATTER_RADIUS, settings.BASE_SCATTER_RADIUS)
            minion_center = (base_center[0] + offset_x, base_center[1] + offset_y)
            minions.append(Enemy(center=minion_center))

        room.enemies.append(guardian)
        room.enemies.extend(minions)
        bases.append({"guardian": guardian, "minions": minions})

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
    enemy_projectiles = []
    return room, player, projectiles, enemy_projectiles, bases


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

    room, player, projectiles, enemy_projectiles, bases = create_game_state()
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
                room, player, projectiles, enemy_projectiles, bases = create_game_state()
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
            # the player does. A guardian never moves, and instead may
            # return a freshly-fired Projectile here (step 27) -- that's
            # the only case update() returns anything but None.
            for enemy in room.enemies:
                new_enemy_projectile = enemy.update(dt, player, room.wall_rects)
                if new_enemy_projectile is not None:
                    enemy_projectiles.append(new_enemy_projectile)

            # Touching an enemy damages the player, unless still
            # invulnerable from a recent hit. take_damage() returns True
            # once health hits 0 -- that's what ends the run. Damage now
            # comes from the enemy itself (enemy.touch_damage) instead of
            # one fixed constant, since a guardian hits harder than a
            # regular enemy.
            player.tick_invulnerability(dt)
            for enemy in room.enemies:
                if player.rect.colliderect(enemy.rect):
                    if player.take_damage(enemy.touch_damage):
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

            # Same idea as the player's projectiles above, but simpler --
            # an enemy projectile only ever needs to check against the
            # PLAYER, never other enemies. take_damage() already handles
            # the invulnerability window internally, so no extra check
            # is needed here for that.
            for enemy_projectile in enemy_projectiles[:]:
                enemy_projectile.update(dt)

                if enemy_projectile.get_rect().colliderect(player.rect):
                    if player.take_damage(enemy_projectile.damage):
                        game_over = True
                    enemy_projectiles.remove(enemy_projectile)
                    continue

                hit_wall = any(
                    enemy_projectile.get_rect().colliderect(wall_rect)
                    for wall_rect in room.wall_rects
                )
                left_map = not room.rect.collidepoint(enemy_projectile.pos)
                if hit_wall or left_map:
                    enemy_projectiles.remove(enemy_projectile)

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
        for enemy_projectile in enemy_projectiles:
            enemy_projectile.draw(game_surface, camera_x, camera_y)

        # Step 29: drawn AFTER every entity above, on purpose -- the
        # "wall" layer (fence/wall tiles) needs to cover the player and
        # enemies when they're standing "in front of" it from the
        # camera's point of view, not sit underneath them like the rest
        # of the map does.
        room.draw_foreground(game_surface, camera_x, camera_y)

        hud.draw_health_bar(game_surface, player)
        hud.draw_weapon_label(game_surface, player)

        # A base still counts as "remaining" if its guardian OR any of
        # its minions are still alive -- clearing one means ALL of them
        # (guardian included) are dead.
        bases_remaining = sum(
            1 for base in bases
            if base["guardian"].health > 0 or any(m.health > 0 for m in base["minions"])
        )
        hud.draw_bases_label(game_surface, bases_remaining, len(bases))

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