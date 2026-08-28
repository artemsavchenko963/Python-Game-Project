"""
Step 21: Room now loads the whole game map from a Tiled .tmx file instead
of generating a rectangular room in code. The old procedural system
(border walls, door gaps, room chain) is gone -- there's just one big
persistent map now.

The whole map is pre-rendered ONCE into a single big background image
when the map loads (self.background). Every frame, draw() just blits the
portion of that image the camera can currently see -- much cheaper than
redrawing thousands of individual tiles every frame, and safe to do
because the map itself never changes while the game is running.

Step 23: wall_rects is now built for real, instead of always being an
empty list. It looks for tiles that have been given a custom boolean
property called "solid" (settings.SOLID_TILE_PROPERTY) inside the Tiny
Slates TILESET in Tiled -- not per map-cell, per actual tile image, so
tagging one water tile solid makes every instance of that tile solid
everywhere it's used across the whole map. Untagged tiles contribute
nothing, so if you haven't tagged anything yet, wall_rects still comes
back empty and movement is still unblocked everywhere -- same safe
fallback as before.

Step 26b: each object on the "enemy" object layer is no longer read as a
single enemy's spawn point -- it's read as the CENTER of a whole BASE.
self.base_spawns is a list of (x, y) points, one per object you've
placed on that layer in Tiled. main.py (step 26c) is what actually turns
each of those points into a guardian plus a scattered group of regular
enemies.

Step 28: _build_wall_rects/_render_background used to loop over one
hardcoded tuple of tile-layer names ("ground", "decoration", "nature",
"boss"). Every time you renamed or added a layer in Tiled (like the
nature -> flor, boss -> wall rename), the game crashed looking for a
layer name that no longer existed. Now both methods just loop over
EVERY tile layer the map actually has, in whatever order Tiled lists
them, and skip anything that isn't a tile layer (object layers like
"spawnpoint"/"enemy" are skipped automatically). Rename or add tile
layers in Tiled as much as you want -- nothing here needs to change to
match.
"""

import pygame
import pytmx
from pytmx.util_pygame import load_pygame

import settings


class Room:
    def __init__(self, tmx_path=None):
        tmx_path = tmx_path or settings.MAP_PATH
        # Step 30: pixelalpha=True tells pytmx to respect each tile
        # image's REAL per-pixel PNG transparency when loading it.
        # Without this, pytmx defaults to ignoring per-pixel alpha (a
        # performance shortcut), so any tile relying on a transparent
        # background -- trees, gravestones, blood splatters -- renders
        # with solid black wherever it should be see-through. Tiled
        # itself always honors real transparency when displaying tiles,
        # which is why the map looked fine there but broken in-game.
        self.tmx_data = load_pygame(tmx_path, pixelalpha=True)

        map_width_px = self.tmx_data.width * self.tmx_data.tilewidth
        map_height_px = self.tmx_data.height * self.tmx_data.tileheight

        # Used everywhere the old code used a room's rect: camera
        # clamping in main.py, and the "did this projectile leave the
        # map" check. It's just the whole map's bounds now.
        self.rect = pygame.Rect(0, 0, map_width_px, map_height_px)

        self.wall_rects = self._build_wall_rects()

        # Same "a room owns its own enemies/items" pattern as before --
        # main.py fills these in right after creating the Room.
        self.enemies = []
        self.items = []

        self.background = self._render_background(map_width_px, map_height_px)

        # Step 29: the "wall" layer (fence/wall tiles) is pulled OUT of
        # the flat background and pre-rendered separately, onto its own
        # surface with real transparency (SRCALPHA) around the tiles
        # that live on it. main.py draws this AFTER the player/enemies
        # each frame, so those tiles visually cover anything standing
        # "behind" them from the camera's point of view.
        self.foreground = self._render_foreground(map_width_px, map_height_px)

        self.player_spawn, self.base_spawns = self._read_spawn_points()

    def _build_wall_rects(self):
        """One Rect per tile that's been tagged solid in Tiled. Checks
        every TILE layer the map has (whatever they're named), since a
        solid tile could in principle live on any of them (water on
        ground, a rock on decoration, etc.). Object layers (like
        "spawnpoint"/"enemy") are skipped -- they have no tile grid to
        scan."""
        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        rects = []
        for layer in self.tmx_data.layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            for ty in range(layer.height):
                for tx in range(layer.width):
                    gid = layer.data[ty][tx]
                    if gid == 0:
                        continue
                    props = self.tmx_data.get_tile_properties_by_gid(gid)
                    if props and props.get(settings.SOLID_TILE_PROPERTY):
                        rects.append(pygame.Rect(tx * tw, ty * th, tw, th))
        return rects

    def _render_background(self, map_width_px, map_height_px):
        """Draw every tile, on every TILE layer EXCEPT the foreground
        ones (settings.FOREGROUND_LAYER_NAMES, e.g. "wall"), once, onto
        one big image -- in the same bottom-to-top order Tiled's Layers
        panel shows them. Whatever tile layers the map has (however
        many, whatever they're named) all get drawn; object layers are
        skipped since they have no tiles to blit."""
        background = pygame.Surface((map_width_px, map_height_px))
        for layer in self.tmx_data.layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            if layer.name in settings.FOREGROUND_LAYER_NAMES:
                continue
            for tx, ty, image in layer.tiles():
                background.blit(image, (tx * self.tmx_data.tilewidth, ty * self.tmx_data.tileheight))
        return background

    def _render_foreground(self, map_width_px, map_height_px):
        """Same idea as _render_background, but ONLY the layers named in
        settings.FOREGROUND_LAYER_NAMES, onto a surface that supports
        real transparency (SRCALPHA) -- everywhere there isn't a fence
        tile has to stay see-through, or the player/enemies would get
        blotted out by an opaque black rectangle instead of just the
        fence tiles covering them."""
        foreground = pygame.Surface((map_width_px, map_height_px), pygame.SRCALPHA)
        for layer in self.tmx_data.layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            if layer.name not in settings.FOREGROUND_LAYER_NAMES:
                continue
            for tx, ty, image in layer.tiles():
                foreground.blit(image, (tx * self.tmx_data.tilewidth, ty * self.tmx_data.tileheight))
        return foreground

    def _read_spawn_points(self):
        """Pull the player's starting position, and every base location,
        out of the map's own object layers. Each object on the 'enemy'
        layer is now a base's center point (see the step 26b note
        above), not a single enemy. Any extra unnamed duplicate object
        left over on a layer is skipped automatically, since only the
        real object has its Class (obj.type) set."""
        player_spawn = None
        base_spawns = []
        for obj in self.tmx_data.objects:
            if obj.type == "player":
                player_spawn = (obj.x, obj.y)
            elif obj.type == "enemy":
                base_spawns.append((obj.x, obj.y))
        return player_spawn, base_spawns

    def draw(self, screen, camera_x, camera_y):
        # Uses the destination surface's own size rather than the
        # settings screen size, since step 22 draws everything onto a
        # smaller internal surface first (for the zoom effect) before
        # that gets scaled up to the real window.
        visible_area = pygame.Rect(camera_x, camera_y, screen.get_width(), screen.get_height())
        screen.blit(self.background, (0, 0), area=visible_area)

    def draw_foreground(self, screen, camera_x, camera_y):
        """Step 29: call this AFTER drawing the player/enemies, not
        before. Same visible-area-blit trick as draw(), just against
        self.foreground (the "wall" layer only) instead of the main
        background -- and since that surface is transparent everywhere
        there's no fence tile, this only actually covers anything up
        where a fence tile really is."""
        visible_area = pygame.Rect(camera_x, camera_y, screen.get_width(), screen.get_height())
        screen.blit(self.foreground, (0, 0), area=visible_area)