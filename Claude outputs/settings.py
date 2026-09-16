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

# --- Weapon pickups (step 20) ---
PICKUP_SIZE = 10
PICKUP_COLOR = (90, 220, 140)         # green -- clearly distinct from enemy red / projectile yellow
PICKUP_BORDER_COLOR = (20, 60, 40)

# --- Tiled map (step 21) ---
# Path to the .tmx file, relative to main.py. "Tiny Slates.tsx" (and
# whatever image it points to) must sit in this same folder, since the
# .tmx references it by a relative path too.
MAP_PATH = "maptailed.tmx"

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
MINE_COLOR = (210, 140, 30)          # orange -- reads as "danger" once revealed
MINE_BORDER_COLOR = (90, 55, 10)
MINE_DAMAGE = 35
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
DIFFICULTIES = {
    "Easy":       {"mines": 130, "castle_enemies": 10, "map_enemies": 0},
    "Mid":        {"mines": 240, "castle_enemies": 20, "map_enemies": 0},
    "Hard":       {"mines": 400, "castle_enemies": 30, "map_enemies": 0},
    "Impossible": {"mines": 600, "castle_enemies": 30, "map_enemies": 60},
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
