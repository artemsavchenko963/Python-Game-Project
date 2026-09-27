"""
Step 1 settings — just enough to open a window.
We'll add more constants here later (colors, speeds, tile size) as we need them.
"""

# These two get OVERWRITTEN at startup (see step 25 in main.py) to match
# whatever resolution the player's monitor actually is, since the game
# now launches full screen. The values here only matter as a fallback,
# before that happens.
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900
FPS = 60

BG_COLOR = (20, 20, 25)  # dark grey, our "underground lab" background for now

# --- Player (step 2) ---
# Shrunk in step 21 so the player reads as roughly "one map tile" (the
# Tiled map's tiles are 16px) instead of towering over the whole map.
PLAYER_SIZE = 16                   # width/height of the square, in pixels
PLAYER_COLOR = (80, 200, 255)      # light blue

# --- Player movement (step 3) ---
PLAYER_SPEED = 250 / 3              # was 250 -- step 24 made it three times slower

# --- Room / camera (step 5) ---
# The room is bigger than the window, so the camera has somewhere to scroll to.
# Both dimensions are exact multiples of TILE_SIZE (see step 6) so the tile
# grid lines up evenly with the room's edges, with no leftover partial tile.
TILE_SIZE = 50
ROOM_WIDTH = 1600                   # 32 tiles wide
ROOM_HEIGHT = 1200                  # 24 tiles tall
ROOM_TILES_WIDE = ROOM_WIDTH // TILE_SIZE
ROOM_TILES_TALL = ROOM_HEIGHT // TILE_SIZE

# --- Tile pattern (step 6) ---
# Floor: a subtle 2-color checkerboard so the ground doesn't look like one
# flat, dead rectangle.
FLOOR_COLOR_A = (35, 35, 45)
FLOOR_COLOR_B = (40, 40, 52)

# Walls: a 1-tile-thick solid border around the room, in its own 2-color
# checkerboard so it visually reads as a different material from the floor.
WALL_COLOR_A = (60, 55, 70)
WALL_COLOR_B = (50, 46, 60)

# --- Doors (step 8) ---
DOOR_SPAN_TILES = 2                # how many tiles tall/wide a doorway gap is
DOOR_ENTRY_MARGIN = 8              # pixels past a doorway you land at when entering a room

# --- Room chain (step 9) ---
NUM_ROOMS = 5                      # how many rooms get generated in a row

# --- Aiming (step 10) ---
AIM_INDICATOR_LENGTH = 14          # how far the aim line pokes out from the player
AIM_INDICATOR_COLOR = (255, 225, 110)   # pale yellow, reads as "this is your weapon"

# --- Shooting (step 11) ---
# Projectile radius/color are shared visuals across all weapons for now --
# only speed/damage/fire-rate vary per weapon (see step 19).
PROJECTILE_RADIUS = 3
PROJECTILE_COLOR = (255, 240, 150)

# --- First enemy (step 13) ---
ENEMY_SIZE = 14
ENEMY_COLOR = (220, 70, 70)         # red -- reads clearly as "hostile" against the floor/wall colors
ENEMY_MAX_HEALTH = 30

# --- Enemy chasing (step 15) ---
ENEMY_SPEED = 120 / 3                 # was 120 -- step 24 made it three times slower too

# --- Player health (step 16) ---
PLAYER_MAX_HEALTH = 100
ENEMY_TOUCH_DAMAGE = 10              # damage taken per hit from touching a REGULAR enemy
                                       # (guardians use GUARDIAN_TOUCH_DAMAGE instead, step 26)
PLAYER_INVULNERABLE_DURATION = 1.0   # seconds of safety after being hit, so contact
                                       # doesn't melt your whole health bar in one overlap
PLAYER_INVULNERABLE_COLOR = (255, 255, 255)  # flashes white while briefly invulnerable

# --- Health bar (step 17) ---
HUD_MARGIN = 20                      # distance from the corner of the window
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 24
HEALTH_BAR_BG_COLOR = (50, 20, 20)      # "empty" portion
HEALTH_BAR_FILL_COLOR = (200, 40, 40)   # "remaining health" portion
HEALTH_BAR_BORDER_COLOR = (10, 10, 10)
HEALTH_BAR_BORDER_WIDTH = 2
HEALTH_BAR_BORDER_RADIUS = 6            # step 54: rounded corners, matches the newer HUD look

# --- HUD panel (step 54) ---
# A single rounded, red-tinted backdrop drawn BEHIND the whole left-side
# stack (health bar, weapon label, bases label, scanner label) -- before
# this they were just plain text floating directly over the game world,
# which is what read as "looks bad." hud.py's draw_hud_panel draws this
# first; every other element in the stack keeps its own existing x/y
# math completely unchanged and just ends up sitting on top of it.
HUD_PANEL_WIDTH = 320
HUD_PANEL_PADDING = 14
HUD_PANEL_ROW_GAP = 8
HUD_PANEL_BG_COLOR = (20, 8, 10, 205)
HUD_PANEL_BORDER_COLOR = (130, 45, 45)
HUD_PANEL_BORDER_RADIUS = 14

# --- Game over (step 18) ---
GAME_OVER_OVERLAY_ALPHA = 180        # 0 = invisible, 255 = fully opaque black overlay
GAME_OVER_TITLE_COLOR = (220, 40, 40)
GAME_OVER_TITLE_FONT_SIZE = 64
HUD_TEXT_COLOR = (230, 230, 230)
GAME_OVER_HINT_FONT_SIZE = 28

# --- Weapons (step 19) ---
# Each weapon is just a different combination of these three numbers.
PISTOL_DAMAGE = 10                  # 3 hits to kill the current 30-HP enemy
PISTOL_FIRE_INTERVAL = 0.25          # 4 shots/sec
PISTOL_PROJECTILE_SPEED = 600

SMG_DAMAGE = 4                       # weaker per hit...
SMG_FIRE_INTERVAL = 0.08             # ...but fires far more often (12.5 shots/sec)
SMG_PROJECTILE_SPEED = 650

WEAPON_LABEL_FONT_SIZE = 22           # HUD text showing which weapon is equipped

# --- Souls (step 52, redesigned step 53) ---
# The shop's currency -- earned by killing enemies (see the "Shop" block
# near the bottom of this file for the actual shop). Shown as its own
# rounded badge top-center of the screen (hud.py's draw_souls_badge),
# not stuffed into the left-side health/weapon/bases stack -- it reads
# more like a persistent currency counter that way, similar to how
# lives/coins sit top-center in a lot of arcade HUDs.
SOULS_PER_ENEMY = 35                  # a regular enemy or castle/map-scattered extra (or a
                                         # boss-fight minion -- see boss.py's reinforcements)
SOULS_PER_GUARDIAN = 100              # a base's guardian ("tower")

SOULS_BADGE_WIDTH = 150                # fixed width (not measured from the text) so the
                                         # badge never subtly resizes/jitters as the number changes
SOULS_BADGE_HEIGHT = 44
SOULS_BADGE_TOP_MARGIN = 20            # distance from the top of the screen
# Step 54: recolored from the original indigo/blue to a deep blood-red --
# matches the game's existing red/black look better than "arcane purple" did.
SOULS_BADGE_BG_COLOR = (32, 10, 12, 222)     # RGBA, deep blood-red
SOULS_BADGE_BORDER_COLOR = (205, 60, 55)
SOULS_BADGE_FONT_SIZE = 26
SOULS_BADGE_TEXT_COLOR = (255, 228, 222)

# The little glowing "soul" icon drawn to the left of the number --
# hud.py's _draw_soul_orb (a solid core plus a soft halo), not an emoji
# or an image file, so it always renders crisply at any size.
SOULS_ICON_RADIUS = 9
SOULS_ICON_COLOR = (215, 35, 35)             # step 54: red, was pale blue
SOULS_ICON_CORE_COLOR = (255, 205, 195)

# --- Weapon pickups (step 20) ---
PICKUP_SIZE = 10
PICKUP_COLOR = (90, 220, 140)         # green -- clearly distinct from enemy red / projectile yellow
PICKUP_BORDER_COLOR = (20, 60, 40)

# --- Tiled map (step 21) ---
# Path to the .tmx file, relative to main.py. "Tiny Slates.tsx" (and
# whatever image it points to) must sit in this same folder, since the
# .tmx references it by a relative path too.
MAP_PATH = "maptailed.tmx"

# --- Arena (second map, step 46) ---
# Clearing every base in the castle map moves the player onto this
# second, separate map instead of showing victory right away -- same
# folder-relative-path rule as MAP_PATH above. Its own spawn point uses
# Class "spawn" rather than "player" in Tiled -- see room.py's
# _read_spawn_points, which reads either name.
ARENA_MAP_PATH = "arena.tmx"

# --- Arena camera zoom (step 49) ---
# The arena map is much smaller (1264x1264 world pixels) than the castle
# map -- on a big enough monitor, the normal camera view (SCREEN_WIDTH/
# HEIGHT divided by the regular ZOOM above) is actually WIDER and/or
# TALLER than the whole arena, so no matter where the camera clamps to,
# there's a strip of "past the edge of the map" background showing on
# one side. main.py handles this by computing a bigger, arena-only zoom
# at the moment it builds the arena (from the real screen size and the
# arena's own room.rect), just large enough that the camera's view never
# exceeds the map in either dimension. This margin is multiplied on top
# of that "just barely fits" zoom so the fit isn't pixel-perfect exact
# (which would leave zero room for the camera to move at all, and risks
# a 1px seam from int() rounding) -- 1.05 means "5% more zoomed in than
# the bare minimum."
ARENA_ZOOM_SAFETY_MARGIN = 1.05

# Step 50: the arena map has no dedicated "boss spawn" object in Tiled --
# main.py just spawns the boss this many world pixels straight above
# wherever the arena's own player spawn point is, which keeps it a
# short, deliberate walk from where the player lands instead of right
# on top of them.
BOSS_SPAWN_OFFSET = 300

# --- Camera zoom (step 22, lowered step 33) ---
# The actual window stays SCREEN_WIDTH x SCREEN_HEIGHT, but the world is
# drawn onto a SMALLER surface internally, then stretched up to fill the
# real window -- that's what makes the camera feel closer to the player:
# a smaller slice of the map now fills the same window space. 2 means
# "everything on screen appears twice as big, half as much map visible."
# Lowered from 2 to 1.5 (step 33) so more of the map is visible around
# the player -- can be any number, including fractions like this one,
# not just whole numbers.
ZOOM = 1.5

# --- Wall collision (step 23) ---
# room.py builds wall_rects by looking for tiles tagged with a custom
# boolean property called "solid" (added per-tile, inside the Tiny
# Slates tileset, in Tiled). This is just the property NAME it looks
# for -- if no tiles have this property set yet, wall_rects comes back
# empty and nothing blocks movement, same as before.
SOLID_TILE_PROPERTY = "solid"

# --- Pause menu (step 25) ---
# The pause button is drawn directly on the real window, NOT on the
# zoomed internal surface, so it stays a fixed, crisp size no matter
# what ZOOM is set to.
PAUSE_BUTTON_SIZE = 44
PAUSE_BUTTON_MARGIN = 20             # distance from the top-right corner
PAUSE_BUTTON_COLOR = (40, 40, 50)
PAUSE_BUTTON_BAR_COLOR = (230, 230, 230)   # the two little bars of the "II" icon

PAUSE_OVERLAY_ALPHA = 170
PAUSE_TITLE_FONT_SIZE = 56

PAUSE_LEAVE_BUTTON_WIDTH = 180
PAUSE_LEAVE_BUTTON_HEIGHT = 56
PAUSE_LEAVE_BUTTON_COLOR = (110, 40, 40)
PAUSE_LEAVE_BUTTON_TEXT_COLOR = (230, 230, 230)
PAUSE_LEAVE_BUTTON_FONT_SIZE = 30

# --- Bases (step 26) ---
# Each object on the map's "enemy" layer marks the CENTER of a base, not
# a single enemy. main.py spawns one tough, stationary guardian exactly
# there, plus a scattered group of regular enemies around it -- clearing
# a base means killing every one of them, guardian included.
BASE_MIN_ENEMIES = 10                # regular enemies spawned per base...
BASE_MAX_ENEMIES = 15                # ...random count in this range
BASE_SCATTER_RADIUS = 50             # was 220 -- 30 would jam 10-15 units almost on
                                       # top of each other; 50 gives enough room to
                                       # still read as one tight camp

AGGRO_RADIUS = 300                   # regular enemies only start chasing once you're this close

GUARDIAN_SIZE = 30
GUARDIAN_COLOR = (150, 30, 130)      # dark magenta -- visually distinct from regular red enemies
GUARDIAN_MAX_HEALTH = 200
GUARDIAN_TOUCH_DAMAGE = 25

GUARDIAN_SHOOT_RANGE = 400           # guardians only fire once you're this close
GUARDIAN_FIRE_INTERVAL = 1.2         # seconds between guardian shots
GUARDIAN_PROJECTILE_SPEED = 400
GUARDIAN_PROJECTILE_DAMAGE = 15

BASES_LABEL_FONT_SIZE = 22            # HUD text showing bases remaining

# --- Foreground layers (step 29) ---
# Tile layers listed here get drawn AFTER the player/enemies each frame,
# instead of being flattened into the one static background image. That's
# what makes a tall object (a fence, a wall top) visually cover the
# player when they're standing "in front of" it from the camera's point
# of view, instead of the player always drawing on top of every tile.
# If you rename the "wall" layer in Tiled later, update the name here to
# match -- everything else in room.py adapts to renames automatically,
# but this one has to name an actual layer on purpose, since it needs to
# know which tiles are "tall enough to draw over the player."
FOREGROUND_LAYER_NAMES = {"wall", "tree"}

# --- Victory (step 32) ---
# Clearing every base (bases_remaining hits 0) now actually means
# something -- a victory screen, same idea as the "YOU DIED" game-over
# screen but the other way around. Font sizes/overlay darkness are
# shared with the game-over screen (GAME_OVER_TITLE_FONT_SIZE,
# GAME_OVER_HINT_FONT_SIZE, GAME_OVER_OVERLAY_ALPHA) -- only the title
# color differs, so it doesn't look like a repeat of dying.
VICTORY_TITLE_COLOR = (90, 220, 130)   # green -- reads as "you won", not "you died"

# --- Fog of war / limited vision (step 34) ---
# A dark, horror-style vignette centered on the player: fully visible
# close up, fading to fully black/hidden further out. Both radii are in
# WORLD pixels (same units as PLAYER_SPEED, AGGRO_RADIUS, etc.) -- ZOOM
# only affects how big things look on screen, not these distances, so
# you don't need to re-tune this if ZOOM changes later.
FOG_COLOR = (0, 0, 0)
FOG_INNER_RADIUS = 220   # fully visible within this distance of the player
FOG_OUTER_RADIUS = 420   # fully black/hidden beyond this distance -- fades in between

# --- Minefield (step 35) ---
# Mines are scattered across the whole map except inside the castle
# (room.castle_rect, read from a rectangle object in Tiled with Class
# "castle") plus a small extra margin, never on top of a solid wall
# tile, and never right on top of where the player starts.
MINE_SIZE = 14                       # was 10 -- a bit bigger, easier to spot/read once revealed
MINE_COLOR = (210, 140, 30)          # orange -- reads as "danger" once revealed -- only
                                       # used as a fallback if MINE_IMAGE_PATH fails to load
MINE_BORDER_COLOR = (90, 55, 10)
MINE_DAMAGE = 35

# Step 40: a real icon (mine.jpg) instead of the plain orange square --
# same idea as the player sprite (step 39): a plain JPEG can't store real
# transparency, so it has a light gray/white checkerboard baked into its
# background pixels instead, which mine.py strips out at load time the
# same way player.py does. Drawn a bit bigger than the actual collision
# rect (MINE_SIZE) so the artwork reads clearly once revealed -- the
# hitbox/collision size is completely unaffected by this.
MINE_IMAGE_PATH = "assets/images/mines/mine.jpg"
MINE_DISPLAY_SIZE = 26
MINE_CHECKER_BRIGHTNESS_THRESHOLD = 175
MINE_COUNT = 90                      # was 40 -- felt sparse across the whole map
MINE_CASTLE_MARGIN = 40              # extra buffer added around the castle rect
MINE_PLAYER_SPAWN_SAFE_RADIUS = 100  # no mine spawns this close to the player's start
MINE_PLACEMENT_ATTEMPTS_PER_MINE = 20   # gives up on a mine after this many bad rolls,
                                          # rather than looping forever on a crowded map

# Mines are invisible by default -- you have to actively scan for them.
# Pressing E triggers a scan: any mine within SCANNER_RADIUS of the
# player becomes visible for SCANNER_REVEAL_DURATION seconds, then goes
# invisible again (it's still there, and still lethal, the whole time --
# only the DRAWING is affected). SCANNER_COOLDOWN is how long you have
# to wait between scans.
SCANNER_RADIUS = 150                  # was 120 -- scan reveals a wider area around you now
SCANNER_REVEAL_DURATION = 6           # was 1.5 -- revealed mines stay visible much longer
SCANNER_COOLDOWN = 2.5                # was 4.0 -- felt too slow to re-scan

# Pressing F defuses the nearest REVEALED mine within this range,
# removing it permanently -- has to actually be lit up from a recent
# scan first, you can't defuse a mine you haven't found yet.
MINE_DEFUSE_RANGE = 150               # was 40 -- can now defuse from much farther away

SCANNER_LABEL_FONT_SIZE = 22          # HUD text showing scan cooldown status

# --- Difficulty select menu (step 36) ---
# Shown once, before the map even loads. Each difficulty controls three
# numbers: how many mines get scattered (replaces the flat MINE_COUNT
# above -- MINE_COUNT itself is now just a fallback, unused once the
# menu has run), how many EXTRA plain enemies (no guardian) get
# scattered inside the castle, and -- Impossible only -- how many MORE
# plain enemies get scattered across the rest of the whole map. None of
# this touches your existing bases/guardians system (the "enemy" points
# you place in Tiled) -- that still works exactly as it always has,
# completely unaffected by difficulty. Order here is display order too.
# Step 50: four more keys per difficulty -- boss_health/boss_damage/
# boss_speed/boss_attack_interval -- read by boss.py's Boss class the
# exact same way Enemy already reads mines/castle_enemies/map_enemies:
# whatever difficulty the player picked at the menu is what the boss in
# the arena scales with too, not a separate/hardcoded set of numbers.
# boss_damage covers BOTH touch damage and each projectile hit (see
# Boss.touch_damage/_shoot) -- one number, two places it's used, same as
# a guardian's own damage isn't literally two different constants
# either. boss_attack_interval is seconds between shots -- LOWER means
# it attacks MORE often ("faster").
DIFFICULTIES = {
    "Easy":       {"mines": 130, "castle_enemies": 10, "map_enemies": 0,
                    "boss_health": 600,  "boss_damage": 20, "boss_speed": 45, "boss_attack_interval": 1.0},
    "Mid":        {"mines": 240, "castle_enemies": 20, "map_enemies": 0,
                    "boss_health": 900,  "boss_damage": 28, "boss_speed": 50, "boss_attack_interval": 0.85},
    "Hard":       {"mines": 400, "castle_enemies": 30, "map_enemies": 0,
                    "boss_health": 1300, "boss_damage": 38, "boss_speed": 55, "boss_attack_interval": 0.7},
    "Impossible": {"mines": 600, "castle_enemies": 30, "map_enemies": 60,
                    "boss_health": 1800, "boss_damage": 50, "boss_speed": 60, "boss_attack_interval": 0.55},
}

MENU_BG_COLOR = (0, 0, 0)
MENU_TITLE_TEXT = "Dark Rooms"
MENU_TITLE_FONT_SIZE = 72
MENU_TITLE_COLOR = (230, 230, 230)
MENU_BUTTON_WIDTH = 280
MENU_BUTTON_HEIGHT = 70
MENU_BUTTON_GAP = 24                  # vertical space between stacked buttons
MENU_BUTTON_COLOR = (40, 40, 50)
MENU_BUTTON_HOVER_COLOR = (75, 75, 95)   # lit up when the mouse is over it
MENU_BUTTON_BORDER_COLOR = (10, 10, 10)
MENU_BUTTON_TEXT_COLOR = (230, 230, 230)
MENU_BUTTON_FONT_SIZE = 34

# --- Instructions screen (step 37) ---
# Shown once, right after a difficulty is picked and before the map loads --
# a black screen of plain text explaining the minefield mechanic (and the
# basic controls), with a "press any key" hint at the bottom. Blocks the
# same way menu.run() does; closing the window here also quits immediately,
# same as closing it at the difficulty menu.
INSTRUCTIONS_TITLE_TEXT = "How to Survive"
INSTRUCTIONS_LINES = [
    "The whole map outside the castle is full of hidden mines.",
    "Mines are invisible until you scan for them -- press E to pulse-scan",
    "the area around you; any mines caught in that pulse light up for a",
    "few seconds, then fade back to invisible (they're still there, and",
    "still lethal, the whole time -- only the drawing is affected).",
    "Scanning has a short cooldown before you can scan again.",
    "",
    "Walking into a mine -- revealed or not -- damages you and destroys it.",
    "Press F near a mine you've just revealed to defuse it safely instead.",
    "",
    "WASD / arrow keys to move, mouse to aim, left click to fire.",
    "Clear every enemy base to win. Good luck.",
]
INSTRUCTIONS_TITLE_FONT_SIZE = 56
INSTRUCTIONS_TITLE_COLOR = (230, 230, 230)
INSTRUCTIONS_LINE_FONT_SIZE = 28
INSTRUCTIONS_LINE_COLOR = (210, 210, 210)
INSTRUCTIONS_LINE_GAP = 12             # vertical space between lines of text
INSTRUCTIONS_HINT_TEXT = "Press any key or click to continue"
INSTRUCTIONS_HINT_FONT_SIZE = 24
INSTRUCTIONS_HINT_COLOR = (150, 150, 150)
INSTRUCTIONS_HINT_MARGIN = 60          # distance from the bottom of the screen

# --- Mine explosion animation (step 38) ---
# Played once wherever a mine actually detonates (the player walked into
# it) -- NOT when it's safely defused with F, since defusing is meant to
# be the quiet, "did it right" outcome. Three frames, one image file each,
# cycled once and then gone. Paths are relative to main.py, same as
# MAP_PATH above.
EXPLOSION_FRAME_PATHS = [
    "assets/images/mines/exp1.png",
    "assets/images/mines/exp2.png",
    "assets/images/mines/exp3.png",
]
EXPLOSION_FRAME_DURATION = 0.08         # seconds each frame stays up (3 frames = ~0.24s total)
EXPLOSION_DISPLAY_SIZE = 70             # frames are scaled (down) to this many world pixels square

# --- Player sprite animation (step 39) ---
# Three hand-drawn walk-cycle frames (player1 = neutral/idle pose,
# player2/player3 = the two stride extremes), replacing the plain
# light-blue square the player used to be drawn as. These are JPEGs, so
# they can't have a real transparent background -- each one instead has
# a light gray/white checkerboard baked into its pixels where the
# background should be. player.py detects and strips that checkerboard
# out at load time (see _remove_checker_background), so nothing extra
# needs to be done to these files by hand.
PLAYER_FRAME_PATHS = [
    "assets/images/person/player1.png",
    "assets/images/person/player2.png",
    "assets/images/person/player3.png",
]
PLAYER_FRAME_DURATION = 0.12            # seconds each walk frame stays up while moving
PLAYER_SPRITE_HEIGHT = 46               # frames are scaled to this world-pixel height,
                                          # width follows automatically to keep each
                                          # frame's own proportions (they're not all
                                          # exactly the same shape)
PLAYER_CHECKER_BRIGHTNESS_THRESHOLD = 175   # grayscale pixels at least this bright are
                                              # treated as checkerboard background, not
                                              # character -- see player.py

# --- Bullet sprite (step 43) ---
# Same situation as the mine/player art -- bullet.png is fully opaque
# (no real alpha channel), with a light gray/white checkerboard drawn
# right into the background pixels instead of true transparency.
# projectile.py strips that out at load time, then rotates its own copy
# once per bullet to match that bullet's (fixed, never-changing) flight
# direction -- the artwork's own default pose (nose pointing right,
# trail behind it to the left) is treated as angle 0.
PROJECTILE_IMAGE_PATH = "assets/images/bullet/bullet.png"
PROJECTILE_SPRITE_LENGTH = 26            # scaled so the artwork's long axis is this many world pixels
PROJECTILE_CHECKER_BRIGHTNESS_THRESHOLD = 175

# --- Enemy hit flash (step 43) ---
ENEMY_HIT_FLASH_COLOR = (255, 255, 255)
ENEMY_HIT_FLASH_DURATION = 0.12          # seconds an enemy stays solid white after being shot

# --- Bullet impact spark (step 44) ---
# Three real frames (a small spark growing into a burst) replacing the
# earlier procedural-glow stand-in from step 43 -- these are fully
# opaque PNGs with a mid-gray two-tone checkerboard baked into the
# background pixels instead of real alpha, same idea as the other art
# assets, just a different (darker) pair of checker tones -- see
# hit_effect.py's _remove_checker_background for why this one needs its
# own two reference colors instead of the simple single-threshold check
# player.py/mine.py/projectile.py use.
HIT_EFFECT_FRAME_PATHS = [
    "assets/images/effects/ef1.png",
    "assets/images/effects/ef2.png",
    "assets/images/effects/ef3.png",
]
HIT_EFFECT_FRAME_DURATION = 0.05          # 3 frames = ~0.15s total, same quick flash as before
HIT_EFFECT_DISPLAY_SIZE = 28              # frames are scaled to this many world pixels square
HIT_EFFECT_CHECKER_COLORS = [102, 139]    # the two checkerboard grays (as brightness values)
HIT_EFFECT_CHECKER_TOLERANCE = 14

# --- Enemy & guardian sprites (step 45) ---
# Regular enemies get a slow 2-frame idle "wiggle" (enemy.png / enemy2.png,
# two slightly different tentacle poses), always cycling regardless of
# whether they're currently chasing -- there's no separate walk vs. idle
# pose in this art. Guardians ("towers") are just tower.png normally,
# switching briefly to tower2.png (a muzzle-flash pose) for
# GUARDIAN_SHOOT_FLASH_DURATION right after they actually fire. All four
# PNGs are fully opaque with the same light gray/white checkerboard
# baked in as the player/mine/bullet art, so they reuse that same
# single-threshold check (see enemy.py's _remove_checker_background).
ENEMY_FRAME_PATHS = [
    "assets/images/enemy/enemy.png",
    "assets/images/enemy/enemy2.png",
]
ENEMY_FRAME_DURATION = 0.35
ENEMY_SPRITE_SIZE = 32                    # world pixels square -- bigger than ENEMY_SIZE's
                                            # hitbox so the art actually reads clearly
GUARDIAN_IMAGE_PATH = "assets/images/enemy/tower.png"
GUARDIAN_SHOOT_IMAGE_PATH = "assets/images/enemy/tower2.png"
GUARDIAN_SHOOT_FLASH_DURATION = 0.15
GUARDIAN_SPRITE_HEIGHT = 64                # scaled by height -- tower.png/tower2.png aren't
                                             # the same aspect ratio (the muzzle-flash pose is
                                             # taller), same approach as the player's frames
ENEMY_SPRITE_CHECKER_BRIGHTNESS_THRESHOLD = 175

# --- Boss fight prompt (step 47) ---
# Clearing every base no longer teleports you into arena.tmx
# automatically -- instead a banner shows up telling you to press E when
# you're ready, and the actual map switch only happens on that keypress
# (main.py). Reuses the E key -- when there's nothing left to scan for,
# pressing E can't mean "scan" anymore anyway, so there's no real
# conflict with the mine scanner.
BOSS_FIGHT_PROMPT_TEXT = "Press E: Boss Fight"
BOSS_FIGHT_PROMPT_FONT_SIZE = 40
BOSS_FIGHT_PROMPT_TEXT_COLOR = (230, 230, 230)
BOSS_FIGHT_PROMPT_BG_COLOR = (40, 10, 10)
BOSS_FIGHT_PROMPT_BG_ALPHA = 190
BOSS_FIGHT_PROMPT_PADDING = 16          # space between the text and the box edge on every side
BOSS_FIGHT_PROMPT_TOP_MARGIN = 78       # distance from the top of the screen -- below the
                                          # souls badge (step 53), which also sits top-center

# --- Arena backstory screen (step 48) ---
# Shown once, right after pressing E on the "Press E: Boss Fight" prompt
# and before the map actually switches to arena.tmx -- same black,
# blocks-until-a-key/click pattern as menu.run_instructions (menu.py's
# run_arena_backstory), just with its own title/lines/hint so the two
# screens can be tuned independently.
ARENA_BACKSTORY_TITLE_TEXT = "THE RIFT OPENS"
ARENA_BACKSTORY_LINES = [
    "With the last base silenced, the castle floor splits open beneath",
    "the throne room -- whatever ruled this place was never IN these walls.",
    "",
    "It waited below, coiled in a scorched, blood-red arena, for someone",
    "strong enough to actually reach it.",
    "",
    "There are no mines past this point. No shadows left to hide in.",
    "Just you, and whatever is still alive down there.",
    "",
    "Once you step through, it doesn't end until one of you does.",
]
ARENA_BACKSTORY_TITLE_FONT_SIZE = 56
ARENA_BACKSTORY_TITLE_COLOR = (200, 40, 40)
ARENA_BACKSTORY_LINE_FONT_SIZE = 28
ARENA_BACKSTORY_LINE_COLOR = (210, 210, 210)
ARENA_BACKSTORY_LINE_GAP = 12
ARENA_BACKSTORY_HINT_TEXT = "Press any key or click to enter the arena"
ARENA_BACKSTORY_HINT_FONT_SIZE = 24
ARENA_BACKSTORY_HINT_COLOR = (150, 150, 150)
ARENA_BACKSTORY_HINT_MARGIN = 60        # distance from the bottom of the screen

# --- Boss (step 50) ---
# The single enemy waiting in the arena, spawned once (boss.py's Boss
# class) right after the arena backstory screen is dismissed. Four hand-
# drawn idle frames, same "opaque PNG with a checkerboard baked in
# instead of real transparency" situation as the player/enemy/tower art
# (see boss.py's own copy of _remove_checker_background).
BOSS_FRAME_PATHS = [
    "assets/images/boss/boss1.1.png",
    "assets/images/boss/boss1.2.png",
    "assets/images/boss/boss1.3.png",
    "assets/images/boss/boss1.4.png",
]
BOSS_FRAME_DURATION = 0.18
BOSS_CHECKER_BRIGHTNESS_THRESHOLD = 175

# Kept modest on purpose -- the source art is a big, detailed portrait
# full of long trailing tentacles, but scaling it up to look "properly
# huge" in-game made it overwhelm the screen. GUARDIAN_SPRITE_HEIGHT
# (64) is the previous biggest thing in the game; the boss is only a
# bit taller than that, not several times bigger.
BOSS_SPRITE_HEIGHT = 90                 # world pixels, scaled by height (step 45's approach)
BOSS_SIZE = 42                          # the actual hitbox -- smaller than the sprite, same
                                          # "art is bigger than what actually collides" idea as
                                          # ENEMY_SIZE/GUARDIAN_SIZE vs their own sprite sizes

BOSS_SHOOT_RANGE = 500                  # always chases (no AGGRO_RADIUS gate) but only
                                          # fires once the player's within this range
BOSS_PROJECTILE_SPEED = 380

# Step 50: once health drops to (or below) this fraction of max_health,
# the boss enrages -- a ONE-WAY switch, checked in Boss.take_damage,
# that never turns back off for the rest of the fight. Raised from 0.2
# to 0.5 (step 54) -- the boss now enrages (bigger, faster, more
# damage, fires more often, red tint) at 50% hp instead of 20%.
BOSS_RAGE_HEALTH_FRACTION = 0.5           # 50% hp
BOSS_RAGE_SIZE_MULTIPLIER = 1.3          # both the sprite AND the hitbox grow by this much
BOSS_RAGE_SPEED_MULTIPLIER = 1.4
BOSS_RAGE_DAMAGE_MULTIPLIER = 1.5        # applies to touch damage AND each projectile hit
BOSS_RAGE_ATTACK_INTERVAL_MULTIPLIER = 0.65  # LOWER = fires more often once enraged
BOSS_RAGE_TINT_COLOR = (255, 40, 40)     # enraged frames are blended toward this color...
BOSS_RAGE_TINT_BLEND = 0.55              # ...by this much (0 = no change, 1 = solid tint color)

# --- Boss health bar (step 54) ---
# A boss-fight-style bar, top-center, shown only while in_arena -- drawn
# on the real screen (like the souls badge/shop panel) so it stays a
# fixed, crisp size regardless of the arena's own zoom. Sits just below
# the souls badge (which ends at 20 + 44 = 64), with a small gap.
BOSS_HEALTH_BAR_WIDTH = 480
BOSS_HEALTH_BAR_HEIGHT = 26
BOSS_HEALTH_BAR_TOP_MARGIN = 74
BOSS_HEALTH_BAR_BG_COLOR = (35, 10, 10, 220)
BOSS_HEALTH_BAR_FILL_COLOR = (200, 30, 30)
BOSS_HEALTH_BAR_ENRAGED_FILL_COLOR = (255, 110, 30)   # step 54: orange once enraged, easy to spot
BOSS_HEALTH_BAR_BORDER_COLOR = (140, 45, 45)
BOSS_HEALTH_BAR_BORDER_WIDTH = 2
BOSS_HEALTH_BAR_BORDER_RADIUS = 8
BOSS_HEALTH_BAR_LABEL_TEXT = "BOSS"
BOSS_HEALTH_BAR_LABEL_FONT_SIZE = 20
BOSS_HEALTH_BAR_LABEL_COLOR = (255, 220, 215)
BOSS_HEALTH_BAR_RAGE_LABEL_TEXT = "ENRAGED"
BOSS_HEALTH_BAR_RAGE_LABEL_COLOR = (255, 130, 60)

# --- Boss minion reinforcements (step 54) ---
# Every so often during the boss fight, a handful of regular enemies
# (the same kind that spawn early in the castle) appear in a ring around
# the boss -- keeps the fight from being a pure 1v1 stare-down. Interval
# shortens once enraged, same "the fight gets worse" idea as the rest of
# the rage bundle.
BOSS_MINION_SPAWN_INTERVAL = 7.0
BOSS_MINION_SPAWN_INTERVAL_ENRAGED = 4.0
BOSS_MINION_SPAWN_COUNT = 5
BOSS_MINION_SPAWN_RADIUS = 140

# --- Shop (step 52, redesigned step 53) ---
# A panel that pops up in the bottom-right corner of the screen the
# moment every castle base is cleared -- the same "bases_cleared"
# condition the "Press E: Boss Fight" prompt already uses -- so there's
# a window to spend whatever souls got earned clearing the castle
# BEFORE walking into the arena. Stays up until the player actually
# enters the arena (hud.py/main.py gate its visibility on bases_cleared
# and not in_arena, same as the boss-fight prompt).
#
# Every entry is a plain dict: "key" (what Player.purchase_shop_item
# switches on and what SHOP_ITEM_COLORS below is keyed by), "name"
# (button label), "cost" (in souls). Each one is one-time-only per run
# -- buying it adds its key to Player.shop_purchases, and a key already
# in there can't be bought again (see purchase_shop_item in player.py).
SHOP_ITEMS = [
    {"key": "speed", "name": "+30% Speed", "cost": 400},
    {"key": "damage", "name": "+50% Damage", "cost": 350},
    {"key": "health", "name": "+40% Max HP", "cost": 295},
    {"key": "relic", "name": "??? Relic", "cost": 600},
]
SHOP_SPEED_MULTIPLIER = 1.30
SHOP_DAMAGE_MULTIPLIER = 1.50
SHOP_HEALTH_MULTIPLIER = 1.40

# The "??? Relic" -- a brand new weapon with stats rolled randomly
# within these ranges the moment it's bought (player.py's
# _make_relic_weapon), instead of one fixed, known set of numbers like
# the Pistol/SMG have. That randomness is the "secret"/"random
# features" the shop promises for it.
SHOP_RELIC_NAME = "??? Relic"
SHOP_RELIC_DAMAGE_RANGE = (8, 40)
SHOP_RELIC_FIRE_INTERVAL_RANGE = (0.05, 0.35)      # seconds between shots -- LOWER is faster
SHOP_RELIC_PROJECTILE_SPEED_RANGE = (500, 900)

# A small color accent per item, used for the little bar on the left
# edge of each button (hud.py's draw_shop) -- purely decorative, just
# makes the four items easier to tell apart at a glance.
SHOP_ITEM_COLORS = {
    "speed": (110, 210, 230),
    "damage": (230, 100, 80),
    "health": (120, 220, 140),
    "relic": (190, 120, 230),
}

# Panel layout -- drawn directly on the real window (like the pause
# button/overlay), not on the zoomed game_surface, so it stays a fixed,
# crisp size and a stable clickable position no matter what zoom is
# currently active on either map. Rounded corners throughout
# (border_radius, pygame 2.x's pygame.draw.rect) instead of the old
# sharp-edged boxes.
SHOP_PANEL_MARGIN = 24                  # distance from the right/bottom edges of the screen
SHOP_PANEL_WIDTH = 340
SHOP_PANEL_BORDER_RADIUS = 14
# Step 54: recolored from indigo/blue to a deep blood-red, matching the
# souls badge's own step 54 recolor and the game's existing red/black look.
SHOP_PANEL_BG_COLOR = (32, 10, 12, 228)      # RGBA, deep blood-red -- matches the souls badge
SHOP_PANEL_BORDER_COLOR = (205, 60, 55)
SHOP_TITLE_TEXT = "SHOP"
SHOP_TITLE_FONT_SIZE = 28
SHOP_TITLE_COLOR = (255, 210, 205)
SHOP_DIVIDER_COLOR = (140, 55, 55)
SHOP_ITEM_FONT_SIZE = 23
SHOP_ITEM_HEIGHT = 56
SHOP_ITEM_GAP = 12                      # vertical space between stacked item buttons
SHOP_PANEL_PADDING = 16                 # space between the panel's edge and its content
SHOP_BUTTON_BORDER_RADIUS = 10
SHOP_BUTTON_ACCENT_WIDTH = 6             # the colored bar on each button's left edge
SHOP_COST_ICON_RADIUS = 6                # smaller version of the souls badge's orb icon,
                                           # shown next to each item's cost

SHOP_BUTTON_COLOR = (38, 36, 55)
SHOP_BUTTON_HOVER_COLOR = (58, 56, 85)
SHOP_BUTTON_DISABLED_COLOR = (28, 26, 34)     # not enough souls yet
SHOP_BUTTON_PURCHASED_COLOR = (28, 55, 40)    # already owned -- green, reads as "done"
SHOP_BUTTON_BORDER_COLOR = (110, 45, 45)      # step 54: red-tinted, was indigo
SHOP_BUTTON_TEXT_COLOR = (230, 230, 240)
SHOP_BUTTON_DISABLED_TEXT_COLOR = (110, 105, 120)
SHOP_BUTTON_PURCHASED_TEXT = "Owned"
SHOP_BUTTON_PURCHASED_TEXT_COLOR = (150, 230, 175)