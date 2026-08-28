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

# --- Camera zoom (step 22) ---
# The actual window stays SCREEN_WIDTH x SCREEN_HEIGHT, but the world is
# drawn onto a SMALLER surface internally, then stretched up to fill the
# real window -- that's what makes the camera feel closer to the player:
# a smaller slice of the map now fills the same window space. 2 means
# "everything on screen appears twice as big, half as much map visible."
ZOOM = 2

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