"""
Step 1 settings — just enough to open a window.
We'll add more constants here later (colors, speeds, tile size) as we need them.
"""

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BG_COLOR = (20, 20, 25)  # dark grey, our "underground lab" background for now

# --- Player (step 2) ---
PLAYER_SIZE = 40                   # width/height of the square, in pixels
PLAYER_COLOR = (80, 200, 255)      # light blue

# --- Player movement (step 3) ---
PLAYER_SPEED = 250                 # pixels per SECOND (not per frame -- see main.py)

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
AIM_INDICATOR_LENGTH = 34          # how far the aim line pokes out from the player
AIM_INDICATOR_COLOR = (255, 225, 110)   # pale yellow, reads as "this is your weapon"