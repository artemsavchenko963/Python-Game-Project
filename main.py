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

Step 32: clearing every base now actually wins the game. `won` works
exactly like `game_over` -- it freezes the update loop (movement,
shooting, chasing, everything) and shows an overlay, just a "VICTORY"
one instead of "YOU DIED", and R restarts from either state. bases_remaining
was already being computed every frame for the HUD counter; this step
just also checks "did that hit 0" and, if there were bases to begin
with, flips `won` to True.

Step 33: ZOOM can now be a fraction (lowered to 1.5) -- view_width/height
now use true division + int(), not integer //, so a non-whole ZOOM still
produces a valid surface size.

Step 34: a dark, radial "fog of war" vignette now sits over the world
every frame -- see the module-level _build_fog_surface() function below
for how it's built (once, at startup, not per-frame -- that would be far
too slow), and the draw section for how it's positioned each frame so
its bright center always lines up with wherever the player is on screen.

Step 35: a minefield. Mines are scattered across the whole map (avoiding
the castle, walls, and the player's spawn -- see _spawn_mines below) and
invisible by default. Pressing E triggers a scan pulse: any mine within
SCANNER_RADIUS of the player becomes visible for a few seconds, then goes
dark again -- still there, still lethal, just not drawn. Pressing F
defuses (removes) the nearest currently-REVEALED mine within
MINE_DEFUSE_RANGE. Neither scanner_cooldown nor mines themselves are
attributes of Player -- they're plain local state right here in main(),
same as `bases`/`projectiles` already are, so none of this needed
touching player.py at all.

Step 36: a difficulty-select menu (menu.py) now runs once before
anything else -- main() blocks on menu.run() first, and whatever
difficulty gets clicked controls how many mines get scattered
(replacing the old flat MINE_COUNT) and how many EXTRA plain enemies
spawn: some confined to the castle (_spawn_castle_enemies, all four
difficulties) and, on Impossible only, more scattered across the rest of
the whole map (_spawn_map_enemies). create_game_state() now takes that
difficulty dict as a parameter instead of reading settings.MINE_COUNT
directly. None of this touches the existing bases/guardians system --
those still come purely from "enemy" points placed in Tiled, same as
always, completely unaffected by difficulty.
"""

import math
import random

import pygame

import settings
from player import Player
from room import Room
from projectile import Projectile
from enemy import Enemy
from mine import Mine
from explosion import Explosion
from hit_effect import HitEffect
from boss import Boss
import boss as boss_module
import menu
import hud
from vhs import VHSOverlay
import sounds
import prefs
import i18n
import settings_menu


def create_game_state(difficulty):
    """Build everything a fresh run needs: the map, every base (a
    stationary guardian plus a scattered group of regular enemies around
    it), the player, the minefield, the difficulty's extra enemies, and
    an empty projectile list. Called once at startup (after the menu
    picks a difficulty) and again every time the player restarts after
    dying -- `difficulty` is one of settings.DIFFICULTIES' value dicts,
    e.g. {"mines": 130, "castle_enemies": 10, "map_enemies": 0}."""
    room = Room()

    # Step 56: building the base list itself now lives in its own
    # helper (_build_bases below) -- the arena (arena.tmx) has its own
    # "enemy"-class objects now too (towers/minions, same as the
    # castle), so main()'s own arena-entry code needs to run this exact
    # same logic a second time, on a different Room.
    bases = _build_bases(room)

    # Player spawns at the map's "spawnpoint" object, same fallback idea.
    player_spawn = room.player_spawn or room.rect.center
    player = Player(center=player_spawn)

    mine_count = difficulty["mines"]
    mines = _spawn_mines(room, player_spawn, mine_count)

    # Step 36: extra plain enemies (no guardian) on top of the existing
    # bases -- some confined to the castle (all four difficulties), and
    # on Impossible, more scattered across the rest of the whole map.
    # Neither group is tracked in `bases`, so they don't affect the
    # "Bases: X/Y" win counter at all -- purely extra danger.
    castle_enemies = _spawn_castle_enemies(room, difficulty["castle_enemies"])
    room.enemies.extend(castle_enemies)

    map_enemies = _spawn_map_enemies(room, difficulty["map_enemies"], player_spawn)
    room.enemies.extend(map_enemies)

    projectiles = []
    enemy_projectiles = []
    return room, player, projectiles, enemy_projectiles, bases, mines


def _build_bases(room):
    """Step 26b (pulled into its own function, step 56): one base per
    "enemy"-class object the map has (room.base_spawns, read by
    room.py's _read_spawn_points) -- a stationary, tanky guardian
    exactly on that point, plus a scattered group of regular enemies
    around it. Returns the same list of {"guardian": ..., "minions":
    [...]} dicts create_game_state's own bases_remaining/"Bases: X/Y"
    counter has always used.

    Step 56: this used to be create_game_state's own inline loop, over
    the CASTLE map only. Pulled out so main()'s arena-entry code (the
    K_e handler) can call it a second time on the arena Room too --
    arena.tmx now has its own "enemy" objects placed in Tiled (towers +
    minions, same as the castle), instead of just the boss standing
    alone. An empty room.base_spawns (nothing placed in Tiled) still
    means zero bases, no substitute fallback -- same reasoning as
    before this was split out."""
    bases = []
    for base_center in room.base_spawns:
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

    return bases


def _spawn_mines(room, player_spawn, mine_count):
    """Step 35 (count now driven by difficulty, step 36): scatter
    `mine_count` mines randomly across the whole map, rejecting a
    candidate spot (and re-rolling a new one) if it falls inside the
    castle (plus a safety margin), on top of a solid wall tile, or too
    close to the player's own starting spot. Gives up on an individual
    mine after MINE_PLACEMENT_ATTEMPTS_PER_MINE bad rolls so a very
    cramped/small map can't hang here forever -- you'd just end up with
    fewer than `mine_count` mines, not a frozen game."""
    castle_rect = room.castle_rect
    if castle_rect is not None:
        avoid_rect = castle_rect.inflate(
            settings.MINE_CASTLE_MARGIN * 2, settings.MINE_CASTLE_MARGIN * 2
        )
    else:
        # No castle object placed in Tiled yet -- nothing to avoid, mines
        # can land anywhere (still subject to the wall/spawn checks
        # below).
        avoid_rect = None

    mines = []
    for _ in range(mine_count):
        for _attempt in range(settings.MINE_PLACEMENT_ATTEMPTS_PER_MINE):
            x = random.uniform(0, room.rect.width)
            y = random.uniform(0, room.rect.height)

            if avoid_rect is not None and avoid_rect.collidepoint(x, y):
                continue

            candidate_rect = pygame.Rect(0, 0, settings.MINE_SIZE, settings.MINE_SIZE)
            candidate_rect.center = (x, y)
            if any(candidate_rect.colliderect(wall_rect) for wall_rect in room.wall_rects):
                continue

            distance_to_spawn = math.hypot(x - player_spawn[0], y - player_spawn[1])
            if distance_to_spawn < settings.MINE_PLAYER_SPAWN_SAFE_RADIUS:
                continue

            mines.append(Mine(center=(x, y)))
            break

    return mines


def _spawn_castle_enemies(room, count):
    """Step 36: `count` EXTRA plain enemies (is_guardian=False), scattered
    randomly INSIDE the castle rectangle -- separate from and in addition
    to the existing bases/guardians system. Falls back to scattering
    across the whole map if no castle rectangle has been placed in Tiled
    yet, same "don't crash on missing data" spirit as everything else
    that reads room.castle_rect."""
    castle_rect = room.castle_rect

    enemies = []
    for _ in range(count):
        for _attempt in range(settings.MINE_PLACEMENT_ATTEMPTS_PER_MINE):
            if castle_rect is not None:
                x = random.uniform(castle_rect.left, castle_rect.right)
                y = random.uniform(castle_rect.top, castle_rect.bottom)
            else:
                x = random.uniform(0, room.rect.width)
                y = random.uniform(0, room.rect.height)

            candidate_rect = pygame.Rect(0, 0, settings.ENEMY_SIZE, settings.ENEMY_SIZE)
            candidate_rect.center = (x, y)
            if any(candidate_rect.colliderect(wall_rect) for wall_rect in room.wall_rects):
                continue

            enemies.append(Enemy(center=(x, y)))
            break

    return enemies


def _spawn_map_enemies(room, count, player_spawn):
    """Step 36 (Impossible only -- count is 0 on every other difficulty,
    so this loop just doesn't run for them): `count` extra plain enemies
    scattered anywhere across the whole map EXCEPT the castle (which
    already gets its own dedicated castle_enemies) -- same avoid-castle/
    avoid-walls/avoid-player-spawn scattering technique as _spawn_mines."""
    castle_rect = room.castle_rect
    if castle_rect is not None:
        avoid_rect = castle_rect.inflate(
            settings.MINE_CASTLE_MARGIN * 2, settings.MINE_CASTLE_MARGIN * 2
        )
    else:
        avoid_rect = None

    enemies = []
    for _ in range(count):
        for _attempt in range(settings.MINE_PLACEMENT_ATTEMPTS_PER_MINE):
            x = random.uniform(0, room.rect.width)
            y = random.uniform(0, room.rect.height)

            if avoid_rect is not None and avoid_rect.collidepoint(x, y):
                continue

            candidate_rect = pygame.Rect(0, 0, settings.ENEMY_SIZE, settings.ENEMY_SIZE)
            candidate_rect.center = (x, y)
            if any(candidate_rect.colliderect(wall_rect) for wall_rect in room.wall_rects):
                continue

            distance_to_spawn = math.hypot(x - player_spawn[0], y - player_spawn[1])
            if distance_to_spawn < settings.MINE_PLAYER_SPAWN_SAFE_RADIUS:
                continue

            enemies.append(Enemy(center=(x, y)))
            break

    return enemies


def _build_fog_surface(view_width, view_height):
    """Step 34: pre-render the radial "fog of war" gradient ONCE at
    startup, not every frame -- computing a soft gradient pixel-by-pixel
    every single frame would tank the framerate. The trick: build a
    small, cheap version of the gradient (SMALL_SIZE x SMALL_SIZE, so the
    pixel-by-pixel loop below is fast), then smoothscale it up to full
    size -- scaling is done in C by pygame, so it's effectively free
    compared to computing every pixel by hand at full resolution.

    view_width/view_height are the zoomed internal game_surface's own
    size. Returns (fog_surface, radius) -- radius is HALF the surface's
    width (and height; it's always square), which the draw loop needs to
    know how far to offset it so the surface's center lands exactly on
    the player's on-screen position.
    """
    # Big enough that even if the player is shoved into a corner of the
    # screen (camera clamped near the map's edge), the fog still reaches
    # every corner of game_surface -- the worst case is the player at
    # one corner and the surface's opposite corner needing to be fully
    # dark, which is exactly game_surface's own diagonal.
    radius = int(math.hypot(view_width, view_height)) + 1
    full_size = radius * 2

    # Compute the gradient at a much smaller size, then scale up -- but
    # DOWNSCALE has to be accounted for when comparing against
    # FOG_INNER_RADIUS/FOG_OUTER_RADIUS below, or the actual on-screen
    # fog distances would depend on the window's resolution instead of
    # staying fixed at whatever those two settings say (in real
    # WORLD-pixel units, same as PLAYER_SPEED/AGGRO_RADIUS/etc).
    downscale = 4
    small_size = max(1, full_size // downscale)
    small_radius = small_size // 2
    small_fog = pygame.Surface((small_size, small_size), pygame.SRCALPHA)
    inner = settings.FOG_INNER_RADIUS
    outer = settings.FOG_OUTER_RADIUS
    for y in range(small_size):
        for x in range(small_size):
            # Scaled back UP by `downscale` so this compares against
            # inner/outer in real world-pixel units, even though we're
            # only actually looping over the small, cheap-to-compute
            # image.
            distance = math.hypot(x - small_radius, y - small_radius) * downscale
            if distance <= inner:
                alpha = 0
            elif distance >= outer:
                alpha = 255
            else:
                alpha = int(255 * (distance - inner) / (outer - inner))
            small_fog.set_at((x, y), (*settings.FOG_COLOR, alpha))

    fog_surface = pygame.transform.smoothscale(small_fog, (full_size, full_size))
    return fog_surface, radius


def main():
    pygame.init()
    pygame.display.set_caption("Dark Rooms")

    # Full screen now, at whatever resolution the monitor actually is --
    # so settings.SCREEN_WIDTH/HEIGHT get overwritten here with the real
    # size instead of the old fixed 1440x900 fallback.
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT = screen.get_size()

    clock = pygame.time.Clock()

    # Step 36: blocks right here until a difficulty button is clicked --
    # nothing about the game itself (Room, Player, mines...) exists yet
    # at this point, on purpose, since the menu is what decides the
    # numbers create_game_state() builds them with. Closing the window
    # from the menu returns None, treated the same as quitting mid-game.
    # Step 64: saved language + volumes, and the mixer, ready BEFORE the
    # start menu so its Settings screen can already play slider previews.
    prefs.load()
    i18n.load()
    sounds.init()
    settings.apply_ui_scale(prefs.get_number(
        "ui_scale", 1.0, settings.UI_SCALE_MIN_FACTOR, settings.UI_SCALE_MAX_FACTOR
    ))

    difficulty_name = menu.run(screen, clock)
    if difficulty_name is None:
        pygame.quit()
        return
    difficulty = settings.DIFFICULTIES[difficulty_name]

    # Step 37: a black instructions screen explaining the minefield
    # mechanic and basic controls, shown once right after the difficulty
    # is picked and before the map loads. Blocks until any key/click,
    # same pattern as the difficulty menu above -- closing the window
    # here also quits immediately instead of continuing into the game.
    if not menu.run_instructions(screen, clock):
        pygame.quit()
        return

    # Step 54: pays the boss's one-time, real per-pixel dekey/scale cost
    # right here -- while the player is already sitting on the black
    # instructions screen for a moment -- instead of the first time a
    # Boss() actually gets constructed, at arena-entry. Without this, that
    # cost (looping over every pixel of 4 full-resolution images) happened
    # synchronously the instant the player pressed E for the boss fight,
    # which is exactly what caused the visible ~3 second freeze.
    boss_module.preload()

    # Step 57: the arena Room itself -- built early and reused later
    # (see the K_e handler further down, which just points `room` at
    # this instead of constructing a fresh one) instead of loading it
    # for the first time at the exact moment the player presses E.
    # Room() parsing the .tmx, pre-rendering the whole background/
    # foreground, and converting the tileset image all cost real,
    # measurable time -- especially now that arena.tmx also carries the
    # ~30 tower/minion spawn points (step 56). That cost used to all
    # happen synchronously right as the player walked into the boss
    # fight, which is exactly what caused the freeze getting reported
    # even after the boss's own art got preloaded above -- the boss
    # wasn't the only expensive thing happening at that moment anymore.
    # Rebuilt fresh every time the castle restarts (the R-key handler
    # below) so a second playthrough in the same session doesn't reuse
    # a Room some earlier run already fought through.
    arena_room = Room(settings.ARENA_MAP_PATH)

    # Step 62: old-TV / VHS overlay -- built once here (it pre-renders
    # scanlines, grain, vignette), drawn every frame right after the world
    # is scaled up. V toggles it.
    vhs_overlay = VHSOverlay(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

    # Step 63: sound effects + quiet looping TV static (sounds.py).
    sounds.start_ambient()
    vhs_enabled = settings.VHS_EFFECT_ENABLED

    # The world is drawn onto this smaller surface, then scaled up to
    # fill the real window each frame -- that's the whole zoom effect
    # (see the step 22 note in the module docstring above). Uses true
    # division + int() rather than // (step 33) so a fractional ZOOM
    # like 1.5 still produces a valid whole-pixel surface size.
    view_width = int(settings.SCREEN_WIDTH / settings.ZOOM)
    view_height = int(settings.SCREEN_HEIGHT / settings.ZOOM)
    game_surface = pygame.Surface((view_width, view_height))

    # Step 49: remembered so a restart (R key, from either game_over or
    # the arena) can put view_width/height/game_surface back to these
    # exact castle-map values -- entering the arena below reassigns all
    # three to a bigger, arena-only zoom, and nothing else ever restores
    # them otherwise.
    castle_view_width, castle_view_height = view_width, view_height

    room, player, projectiles, enemy_projectiles, bases, mines = create_game_state(difficulty)
    explosions = []  # step 38: one per mine that's actually detonated, not defused
    hit_effects = []  # step 43: one per bullet that actually hit something
    game_over = False
    player_death_sound_played = False
    won = False  # step 32: True once every base has been cleared
    in_arena = False  # step 46: True once the castle's cleared and the player's moved to arena.tmx
    paused = False
    stats_open = False  # step 60: toggled by the stats button next to pause
    scanner_cooldown = 0.0  # step 35: seconds left before E can scan again
    # Step 58: counts down from settings.TOWER_INTRO_PROMPT_DURATION,
    # only while the game is actually running (see the update section
    # below) -- drives the one-time "Destroy all N towers" hint.
    tower_prompt_timer = settings.TOWER_INTRO_PROMPT_DURATION

    dt = 0  # time (seconds) since the last frame; updated at the end of each loop
    running = True
    while running:
        # Step 47: computed before the event loop (not just inside the
        # update section below) because the E-key handler needs to know
        # "are all bases down" too, to decide whether E means "enter the
        # boss fight" instead of its usual "scan for mines" -- see the
        # K_e branch just below.
        #
        # Step 58: only the GUARDIAN (tower) has to be dead -- minions
        # scattered around a base no longer block the shop/boss fight at
        # all, they're purely optional extra souls/xp for players who
        # want to farm them. Used to also require every minion dead too
        # (`and all(m.health <= 0 for m in base["minions"])`).
        bases_cleared = bases and all(base["guardian"].health <= 0 for base in bases)

        # 1. Handle input/events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_v:
                vhs_enabled = not vhs_enabled
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not game_over and not won:
                # Esc pauses / resumes (same as the pause button and Continue).
                paused = not paused
            elif event.type == pygame.KEYDOWN and (game_over or won) and event.key == pygame.K_r:
                # Restarting keeps the SAME difficulty you picked at the
                # menu -- it does not send you back to the menu screen.
                room, player, projectiles, enemy_projectiles, bases, mines = create_game_state(difficulty)
                explosions = []
                hit_effects = []
                game_over = False
                player_death_sound_played = False
                won = False
                in_arena = False
                scanner_cooldown = 0.0
                tower_prompt_timer = settings.TOWER_INTRO_PROMPT_DURATION
                # Step 57: a fresh, untouched arena Room ready for this new
                # playthrough -- the old one (if this run had gotten that
                # far) may have had its bases/boss fought through and
                # removed from its enemies list, so it can't just be
                # reused as-is for a second trip through the castle.
                arena_room = Room(settings.ARENA_MAP_PATH)
                # Step 49: undo the arena-only zoom-in (if the run that
                # just ended had gotten that far) -- restarting always
                # puts you back on the castle map, which needs its own,
                # normal view size back.
                view_width, view_height = castle_view_width, castle_view_height
                game_surface = pygame.Surface((view_width, view_height))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not paused and hud.get_pause_button_rect(screen).collidepoint(event.pos):
                    paused = True
                elif not paused and hud.get_stats_button_rect(screen).collidepoint(event.pos):
                    stats_open = not stats_open
                elif paused and hud.get_continue_button_rect(screen).collidepoint(event.pos):
                    paused = False
                elif paused and hud.get_settings_button_rect(screen).collidepoint(event.pos):
                    # Step 64: Settings opens on top of the frozen game. It
                    # blocks (own loop) and shares `clock`, so unpausing
                    # afterwards doesn't see a huge dt.
                    if not settings_menu.run(screen, clock, background=screen.copy()):
                        running = False
                elif paused and hud.get_leave_button_rect(screen).collidepoint(event.pos):
                    running = False
                elif (
                    not paused and not game_over and not won
                    and bases_cleared and not in_arena
                ):
                    # Step 52: the shop panel is only up during this same
                    # window (see hud.draw_shop's own gating in the draw
                    # section below) -- purchase_shop_item already no-ops
                    # safely on a click that can't afford/already owns an
                    # item, so there's nothing else to check here besides
                    # "did this click actually land on one of the buttons."
                    for item, rect in hud.get_shop_button_rects(screen):
                        if rect.collidepoint(event.pos):
                            player.purchase_shop_item(item)
                            break
            elif (
                event.type == pygame.KEYDOWN
                and not game_over and not won and not paused
                and event.key == pygame.K_e
            ):
                if bases_cleared and not in_arena:
                    # Step 47: this used to happen automatically the
                    # instant the last base fell. Now it waits for the
                    # player to actually press E (the on-screen "Press E:
                    # Boss Fight" prompt is what tells them this is
                    # possible -- see hud.draw_boss_fight_prompt in the
                    # draw section below), so they can finish looting/
                    # exploring the castle first instead of being yanked
                    # into the arena the moment the fight ends.
                    #
                    # Step 48: a black backstory screen shown first --
                    # blocks right here (its own tiny event loop, same as
                    # menu.run/run_instructions at startup) until the
                    # player presses a key or clicks. Closing the window
                    # during it quits immediately instead of continuing
                    # into the arena.
                    if not menu.run_arena_backstory(screen, clock):
                        running = False
                    else:
                        # Step 57: reuse the arena Room built early
                        # (right after the instructions screen, or right
                        # after the last restart -- see arena_room's own
                        # comment up there) instead of constructing a
                        # fresh one here. This is the whole fix for the
                        # boss-fight-entry freeze -- Room() parsing the
                        # .tmx and pre-rendering the background/
                        # foreground is real, measurable work, and it
                        # used to all happen right at this exact moment.
                        room = arena_room

                        # Step 56: arena.tmx now has its own "enemy"-class
                        # objects placed in Tiled -- towers (guardians)
                        # plus a scattered group of regular enemies
                        # around each one, exactly the same setup the
                        # castle map's own bases use (_build_bases is the
                        # very same function create_game_state calls).
                        # Reassigning `bases` here replaces the castle's
                        # (already fully cleared, or this prompt couldn't
                        # have fired) bases list with the arena's own --
                        # the "Bases: X/Y" HUD counter and this same
                        # bases_cleared check now track the arena's
                        # fight instead. Victory still only fires once
                        # room.enemies is completely empty (further down,
                        # the "in_arena and not room.enemies" check), so
                        # every arena tower/minion has to die too, not
                        # just the boss.
                        bases = _build_bases(room)

                        if room.player_spawn is not None:
                            player.rect.center = room.player_spawn
                            player.pos = pygame.Vector2(player.rect.topleft)
                        mines = []
                        projectiles = []
                        enemy_projectiles = []
                        explosions = []
                        hit_effects = []
                        in_arena = True

                        # Step 49: the arena (1264x1264 world pixels) is
                        # much smaller than the castle map -- at the
                        # normal ZOOM, a big enough monitor's usual view
                        # is wider and/or taller than the whole arena, so
                        # the camera clamp below always leaves a strip of
                        # "off the edge of the map" background showing on
                        # one side no matter where the player stands (see
                        # settings.ARENA_ZOOM_SAFETY_MARGIN's comment).
                        # Zoom in just far enough, here and only here,
                        # that the view can never exceed the arena's own
                        # size in either dimension, and rebuild
                        # game_surface at that new (smaller) size --
                        # everything downstream (camera math, drawing,
                        # the final scale-up to the real window) already
                        # just reads whatever view_width/view_height and
                        # game_surface currently are.
                        fit_zoom_x = settings.SCREEN_WIDTH / room.rect.width
                        fit_zoom_y = settings.SCREEN_HEIGHT / room.rect.height
                        arena_zoom = max(
                            settings.ZOOM,
                            max(fit_zoom_x, fit_zoom_y) * settings.ARENA_ZOOM_SAFETY_MARGIN,
                        )
                        view_width = max(1, int(settings.SCREEN_WIDTH / arena_zoom))
                        view_height = max(1, int(settings.SCREEN_HEIGHT / arena_zoom))
                        game_surface = pygame.Surface((view_width, view_height))

                        # Step 50: the boss itself -- spawned a fixed
                        # distance above wherever the arena's own spawn
                        # point put the player (arena.tmx has no
                        # dedicated "boss spawn" object of its own).
                        # Added straight into room.enemies rather than
                        # tracked separately -- Boss implements the same
                        # rect/touch_damage/take_damage/update/draw
                        # interface Enemy does, so every loop below that
                        # already knows how to chase-collide/take a
                        # projectile hit/draw "an enemy" just works on it
                        # unchanged. See the "in_arena and not
                        # room.enemies" check further down for how its
                        # death is what finally triggers victory.
                        if room.player_spawn is not None:
                            boss_spawn = (
                                room.player_spawn[0],
                                max(0, room.player_spawn[1] - settings.BOSS_SPAWN_OFFSET),
                            )
                        else:
                            boss_spawn = room.rect.center
                        room.enemies.append(Boss(center=boss_spawn, difficulty=difficulty))
                elif scanner_cooldown <= 0:
                    # Step 35: a scan pulse -- only does anything once the
                    # cooldown has actually reached 0. Any mine currently
                    # within SCANNER_RADIUS of the player gets revealed for
                    # SCANNER_REVEAL_DURATION seconds; mines farther away are
                    # untouched (they'll need a closer scan of their own).
                    for mine in mines:
                        distance = math.hypot(
                            mine.rect.centerx - player.rect.centerx,
                            mine.rect.centery - player.rect.centery,
                        )
                        if distance <= settings.SCANNER_RADIUS:
                            mine.reveal()
                    scanner_cooldown = settings.SCANNER_COOLDOWN
            elif (
                event.type == pygame.KEYDOWN
                and not game_over and not won and not paused
                and event.key == pygame.K_f
            ):
                # Defuses the CLOSEST revealed mine within
                # MINE_DEFUSE_RANGE, if any -- a mine that's still
                # invisible (hasn't been scanned recently) can't be
                # defused, on purpose, since you shouldn't be able to
                # remove a mine you haven't actually found yet.
                closest_mine = None
                closest_distance = None
                for mine in mines:
                    if not mine.is_revealed:
                        continue
                    distance = math.hypot(
                        mine.rect.centerx - player.rect.centerx,
                        mine.rect.centery - player.rect.centery,
                    )
                    if distance <= settings.MINE_DEFUSE_RANGE:
                        if closest_distance is None or distance < closest_distance:
                            closest_mine = mine
                            closest_distance = distance
                if closest_mine is not None:
                    mines.remove(closest_mine)

        # 2. Update game state -- entirely skipped once game_over is True,
        # OR won is True (step 32), OR the game is paused, which is what
        # makes the world freeze in place instead of continuing to move
        # behind whichever overlay is showing.
        player_moved = False
        if not game_over and not won and not paused:
            # Step 46/47: clearing every base in the castle used to show
            # victory right away, then (step 46) teleported into arena.tmx
            # automatically. Now (step 47) the teleport itself only
            # happens when the player actually presses E -- see the K_e
            # handler up in the event loop -- `bases_cleared` up there is
            # what the on-screen prompt below is keyed off of too. Victory
            # itself is still deferred to some later condition IN the
            # arena (not decided yet), so `won` is never set here.

            keys = pygame.key.get_pressed()
            position_before = player.rect.center
            player.handle_movement(dt, keys, room.wall_rects, room.rect)
            player_moved = player.rect.center != position_before
            player.handle_weapon_switch(keys)

            # Step 35: cooldown ticks down regardless of whether a scan
            # is currently in flight; mines tick their own reveal timer
            # down the same way projectiles/enemies already update
            # themselves every frame.
            scanner_cooldown = max(0.0, scanner_cooldown - dt)
            # Step 58: the "Destroy all N towers" hint's own countdown --
            # only ticks while the game is genuinely running, same as
            # scanner_cooldown just above, so pausing doesn't quietly eat
            # into the few seconds it's shown for.
            tower_prompt_timer = max(0.0, tower_prompt_timer - dt)
            for mine in mines:
                mine.update(dt)
            for explosion in explosions:
                explosion.update(dt)
            explosions = [explosion for explosion in explosions if not explosion.is_finished]
            for hit_effect in hit_effects:
                hit_effect.update(dt)
            hit_effects = [hit_effect for hit_effect in hit_effects if not hit_effect.is_finished]

            # A mine is lethal whether or not it's currently visible --
            # only the drawing cares about is_revealed, collision
            # doesn't. Looping over mines[:] since we remove from the
            # real list mid-loop, same reasoning as room.items above.
            for mine in mines[:]:
                if player.rect.colliderect(mine.rect):
                    if player.take_damage(settings.MINE_DAMAGE):
                        game_over = True
                    explosions.append(Explosion(mine.rect.center))
                    sounds.play("mine", settings.SOUND_VOLUME_MINE, "mine")
                    mines.remove(mine)

            # Chase behavior: every enemy on the map moves toward the
            # player each frame, colliding with the map's walls just like
            # the player does. A guardian never moves, and instead may
            # return a freshly-fired Projectile here (step 27) -- that's
            # the only case update() returns anything but None.
            # Step 54: room.enemies[:] -- a snapshot copy -- since the
            # Boss branch below can append fresh minions straight into
            # room.enemies mid-loop (reinforcements); iterating a copy
            # means a minion that just spawned this frame waits until
            # next frame to get its own update() call, rather than
            # potentially being visited twice (once here, once because
            # the live list grew under the loop).
            for enemy in room.enemies[:]:
                new_enemy_projectile = enemy.update(dt, player, room.wall_rects)
                if new_enemy_projectile is not None:
                    enemy_projectiles.append(new_enemy_projectile)
                    shot_distance = pygame.Vector2(enemy.rect.center).distance_to(player.rect.center)
                    if shot_distance <= settings.SOUND_ENEMY_SHOT_MAX_DISTANCE:
                        sounds.play("attack3", settings.SOUND_VOLUME_ENEMY_SHOT, "enemy_shot")
                if isinstance(enemy, Boss) and enemy.pending_minion_spawns:
                    for spawn_center in enemy.pending_minion_spawns:
                        room.enemies.append(Enemy(center=spawn_center))
                    enemy.pending_minion_spawns = []

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

            player.handle_aim(camera_x, camera_y, view_width, view_height, dt)

            # Fire while LMB is held, at most once every
            # equipped_weapon.fire_interval seconds.
            player.tick_cooldown(dt)
            mouse_buttons = pygame.mouse.get_pressed()
            left_button_held = mouse_buttons[0]
            if left_button_held and player.can_fire():
                weapon = player.equipped_weapon
                # Step 52: the shop's "+50% Damage" item is a flat
                # multiplier on top of whatever weapon is equipped --
                # 1.0 (no change) until it's actually bought.
                projectiles.append(
                    Projectile(
                        player.rect.center,
                        player.aim_dir,
                        weapon.projectile_speed,
                        weapon.damage * player.damage_multiplier,
                    )
                )
                player.reset_fire_cooldown()
                sounds.play_player_shot(settings.SOUND_VOLUME_PLAYER_SHOT)

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
                    hit_effects.append(HitEffect(projectile.pos))
                    if hit_enemy.take_damage(projectile.damage):
                        room.enemies.remove(hit_enemy)
                        sounds.play("death", settings.SOUND_VOLUME_ENEMY_DEATH, "enemy_death")
                        # Step 52: souls for the kill -- isinstance guards
                        # this against the boss (a separate class, not an
                        # Enemy) so beating it doesn't also hand out a
                        # regular kill's worth of souls on top of ending
                        # the run in victory. Step 55: xp works the same
                        # way, right alongside it -- every kill (regular
                        # enemy, guardian, boss-fight reinforcement, or
                        # the boss itself) feeds Player.add_experience,
                        # which levels the player up on its own once
                        # there's enough banked.
                        if isinstance(hit_enemy, Enemy):
                            reward = settings.SOULS_PER_GUARDIAN if hit_enemy.is_guardian else settings.SOULS_PER_ENEMY
                            player.add_souls(reward)
                            xp_reward = (
                                settings.LEVEL_XP_PER_GUARDIAN_KILL if hit_enemy.is_guardian
                                else settings.LEVEL_XP_PER_ENEMY_KILL
                            )
                            player.add_experience(xp_reward)
                        else:
                            player.add_experience(settings.LEVEL_XP_PER_BOSS_KILL)
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
                    hit_effects.append(HitEffect(enemy_projectile.pos))
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

            # Step 50: the boss is the only thing ever in room.enemies
            # while in_arena -- once the projectile-hit loop above has
            # killed it (and removed it from room.enemies, same as any
            # other enemy), the arena is empty and that's what finally
            # answers "what wins the game" left open since step 46.
            if in_arena and not room.enemies:
                won = True

        # Step 63: footsteps only while actually walking (not paused/dead),
        # and the player's own death sound exactly once per death.
        sounds.set_moving(player_moved)
        if game_over and not player_death_sound_played:
            player_death_sound_played = True
            sounds.play("death", settings.SOUND_VOLUME_PLAYER_DEATH, "player_death")

        # 3. Draw everything -- always runs, game over or not, so the
        # frozen world stays visible underneath the game-over overlay.
        # Everything draws onto game_surface (the smaller, zoomed-in
        # surface), never directly onto the real window.
        game_surface.fill(settings.BG_COLOR)
        room.draw(game_surface, camera_x, camera_y)
        for item in room.items:
            item.draw(game_surface, camera_x, camera_y)
        for mine in mines:
            mine.draw(game_surface, camera_x, camera_y)
        for enemy in room.enemies:
            enemy.draw(game_surface, camera_x, camera_y)
        player.draw(game_surface, camera_x, camera_y)
        for projectile in projectiles:
            projectile.draw(game_surface, camera_x, camera_y)
        for enemy_projectile in enemy_projectiles:
            enemy_projectile.draw(game_surface, camera_x, camera_y)
        for explosion in explosions:
            explosion.draw(game_surface, camera_x, camera_y)
        for hit_effect in hit_effects:
            hit_effect.draw(game_surface, camera_x, camera_y)

        # Step 29: drawn AFTER every entity above, on purpose -- the
        # "wall" layer (fence/wall tiles) needs to cover the player and
        # enemies when they're standing "in front of" it from the
        # camera's point of view, not sit underneath them like the rest
        # of the map does.
        room.draw_foreground(game_surface, camera_x, camera_y)

        # Step 59: the fog-of-war vignette is gone -- the player now sees
        # the whole screen everywhere (castle and arena alike). The
        # _build_fog_surface helper above is left in place, unused, in
        # case it ever comes back.

        hud.draw_hud_panel(game_surface)
        hud.draw_level_bar(game_surface, player)

        # Step 58: a base now counts as "remaining" purely by whether its
        # TOWER (guardian) is still alive -- minions no longer matter
        # for this count at all, matching bases_cleared's own change
        # above (they're optional extra souls/xp, not a requirement).
        bases_remaining = sum(1 for base in bases if base["guardian"].health > 0)
        hud.draw_bases_label(game_surface, bases_remaining, len(bases))
        hud.draw_scanner_label(game_surface, scanner_cooldown)

        # Step 58: the one-time "Destroy all N towers" hint -- only
        # while in the castle (not in_arena) and only until its own
        # timer runs out; hud.draw_tower_intro_prompt no-ops on its own
        # once that hits 0, but the in_arena guard here keeps it from
        # ever showing on the arena's own, differently-zoomed surface.
        if not in_arena:
            hud.draw_tower_intro_prompt(game_surface, len(bases), tower_prompt_timer)

        # Step 46: clearing every base no longer sets `won` here -- see
        # the in_arena check up in the update section. bases_remaining
        # is still tracked/shown above purely for the HUD label.

        # Step 47: the "Press E: Boss Fight" banner -- only makes sense to
        # show once (every base is down, haven't already gone through)
        # and while there's still a normal game to look at (not already
        # showing the death/victory/pause overlay).
        if bases_cleared and not in_arena and not game_over and not won and not paused:
            hud.draw_boss_fight_prompt(game_surface)

        if game_over:
            hud.draw_game_over(game_surface)
        elif won:
            hud.draw_victory(game_surface)

        # Stretch the finished frame up to fill the real window -- this
        # one line is what actually makes everything look "zoomed in".
        pygame.transform.scale(game_surface, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), screen)

        # VHS / old-TV layer: over the world, under the crisp HUD.
        if vhs_enabled:
            vhs_overlay.update(dt)
            vhs_overlay.draw(screen)

        # Pause button/overlay draw directly on the real window, AFTER
        # the zoomed world is stretched onto it -- so they sit on top of
        # everything, and stay a fixed size no matter what ZOOM is.
        hud.draw_pause_button(screen)
        hud.draw_stats_button(screen, stats_open)
        if stats_open and not paused:
            hud.draw_stats_panel(screen, player)
        if paused:
            hud.draw_pause_overlay(screen)

        # Step 53: the souls badge -- same "draw on the real screen, not
        # game_surface" reasoning as the pause button, so it stays a
        # crisp, fixed size top-center no matter which map's zoom is
        # currently active, instead of getting stretched along with
        # everything else drawn on the zoomed internal surface. Always
        # visible (not gated on bases_cleared like the shop below) --
        # it's a persistent currency counter, same idea as the health bar.
        hud.draw_souls_badge(screen, player)

        # Step 55: the XP progress strip -- bottom-center, always
        # visible (same "persistent counter" reasoning as the souls
        # badge above), drawn on the real screen so it stays a fixed,
        # crisp size no matter which map's zoom is currently active.
        hud.draw_health_bar(screen, player)

        # Step 54: the boss health bar -- top-center, just below the souls
        # badge, shown only while in_arena. There's no dedicated `boss`
        # variable tracked through the whole game loop -- it's just found
        # fresh each frame the same way the isinstance(..., Boss) checks
        # elsewhere already work, since the boss is the only Boss instance
        # that's ever in room.enemies.
        if in_arena:
            current_boss = next((enemy for enemy in room.enemies if isinstance(enemy, Boss)), None)
            if current_boss is not None:
                hud.draw_boss_health_bar(screen, current_boss)

        # Step 52: the shop panel -- same reasoning as the pause button
        # for drawing it on the real `screen` rather than game_surface:
        # its buttons need to stay a fixed, clickable size regardless of
        # which map's zoom is currently active, and event.pos from
        # MOUSEBUTTONDOWN is always in real window coordinates, which
        # only lines up with get_shop_button_rects if this is drawn here
        # too. Same visibility window as the boss-fight prompt.
        if bases_cleared and not in_arena and not game_over and not won and not paused:
            hud.draw_shop(screen, player)

        pygame.display.flip()

        # 4. Wait so we run at a steady FPS, and remember how long that frame
        #    actually took (dt), for next frame's movement math.
        dt = clock.tick(settings.FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()