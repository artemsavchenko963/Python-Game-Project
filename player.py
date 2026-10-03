"""
Player: holds the player's rect (world position + size) and knows how to
move itself (with real wall collision) and draw itself.
"""

import random

import pygame

import prefs
import settings
from weapon import Weapon


def _make_relic_weapon():
    """Step 52: the shop's 600-soul "??? Relic" -- a brand new weapon
    with randomly rolled stats (within settings.SHOP_RELIC_*_RANGE),
    rolled once at the moment it's bought. That's the "random features"
    the relic promises: you don't know whether you're getting a fast,
    weak popgun or a slow, devastating cannon until you actually buy it."""
    damage = random.uniform(*settings.SHOP_RELIC_DAMAGE_RANGE)
    fire_interval = random.uniform(*settings.SHOP_RELIC_FIRE_INTERVAL_RANGE)
    projectile_speed = random.uniform(*settings.SHOP_RELIC_PROJECTILE_SPEED_RANGE)
    return Weapon(settings.SHOP_RELIC_NAME, damage, fire_interval, projectile_speed)


# Step 39: the three walk-cycle frames, loaded and cleaned up ONCE and
# shared by every Player -- there's only ever one player, but this also
# means restarting (step 36's R key) doesn't reload/reprocess the same
# three images from disk again.
_frames = None
_flash_frames = None


def _remove_checker_background(surface):
    """player1/2/3.jpg are plain JPEGs, which can't store real
    transparency -- whatever tool exported them baked a light gray/white
    checkerboard into the pixels where the background should be instead.
    This walks every pixel and turns anything that's both (a) close to
    gray (r, g and b all near each other) and (b) bright enough to be
    checker rather than character (see settings.PLAYER_CHECKER_
    BRIGHTNESS_THRESHOLD) fully transparent. The character art itself is
    either very dark (the cloak) or has actual color in it (red eyes,
    warm skin tones), so it never gets caught by this."""
    surface = surface.convert_alpha()
    width, height = surface.get_size()
    surface.lock()
    for x in range(width):
        for y in range(height):
            r, g, b, a = surface.get_at((x, y))
            brightness = (r + g + b) / 3
            is_grayish = abs(r - g) <= 8 and abs(g - b) <= 8 and abs(r - b) <= 8
            if is_grayish and brightness >= settings.PLAYER_CHECKER_BRIGHTNESS_THRESHOLD:
                surface.set_at((x, y), (r, g, b, 0))
    surface.unlock()
    return surface


def _make_flash_frame(frame):
    """A white silhouette of a frame (every visible pixel turned white,
    same alpha shape) -- alternated with the normal frame while
    invulnerable, for the same 'flashing' effect the plain color square
    used to get from PLAYER_INVULNERABLE_COLOR."""
    flash = frame.copy()
    width, height = flash.get_size()
    flash.lock()
    for x in range(width):
        for y in range(height):
            r, g, b, a = flash.get_at((x, y))
            if a > 0:
                flash.set_at((x, y), (255, 255, 255, a))
    flash.unlock()
    return flash


def _load_frame(path):
    image = pygame.image.load(path)

    # Step 41: PLAYER_FRAME_PATHS now points at real PNGs with a proper
    # alpha channel (no baked-in checkerboard to strip) instead of the
    # old JPEGs -- but _remove_checker_background is harmless to keep
    # around for anyone who swaps a frame back to a plain JPEG later, so
    # branch on the file extension rather than deleting it.
    if path.lower().endswith((".jpg", ".jpeg")):
        image = _remove_checker_background(image)
    else:
        image = image.convert_alpha()

    # These new PNGs are big canvases with a lot of empty transparent
    # space padded around the actual artwork (so the different poses
    # don't all have to be the same canvas size) -- trim down to just
    # the drawn pixels first, or scaling to PLAYER_SPRITE_HEIGHT would
    # scale the whole mostly-empty canvas and the character would come
    # out tiny. get_bounding_rect() finds that content box directly from
    # the alpha channel.
    bounding_rect = image.get_bounding_rect()
    if bounding_rect.width > 0 and bounding_rect.height > 0:
        image = image.subsurface(bounding_rect).copy()

    width, height = image.get_size()
    scale = settings.PLAYER_SPRITE_HEIGHT / height
    new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return pygame.transform.smoothscale(image, new_size)


def _get_frames():
    global _frames, _flash_frames
    if _frames is None:
        _frames = [_load_frame(path) for path in settings.PLAYER_FRAME_PATHS]
        _flash_frames = [_make_flash_frame(frame) for frame in _frames]
    return _frames, _flash_frames


class Player:
    def __init__(self, center):
        self.rect = pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE)
        self.rect.center = center

        # The "real" position, at full float precision. self.rect.x/y can
        # only ever hold whole pixels, so movement math happens here
        # instead and only gets rounded into the rect afterward -- see
        # the note in handle_movement for why this matters.
        self.pos = pygame.Vector2(self.rect.topleft)

        # Which way the player is currently facing/aiming, as a unit
        # vector (length 1). Defaults to facing right. This will be the
        # direction projectiles travel once we add shooting next step.
        self.aim_dir = pygame.Vector2(1, 0)

        # Every weapon the player currently has, plus which one is active.
        # Starts with just the Pistol -- other weapons are earned by
        # walking over a WeaponPickup in the world (step 20).
        self.weapons = [
            Weapon("Pistol", settings.PISTOL_DAMAGE, settings.PISTOL_FIRE_INTERVAL, settings.PISTOL_PROJECTILE_SPEED),
        ]
        self.weapon_index = 0

        # Counts down to 0; the player may fire again once it reaches 0.
        # Starts at 0 so you can fire immediately on the very first frame.
        self.fire_cooldown = 0.0

        self.max_health = settings.PLAYER_MAX_HEALTH
        self.health = self.max_health

        # Counts down to 0; while above 0, take_damage() does nothing.
        # This is what stops standing inside an enemy from draining your
        # whole health bar in a single second.
        self.invulnerable_timer = 0.0

        # Step 39: walk-cycle animation state. frame index 0 is the
        # neutral/idle pose (player1.jpg) -- shown whenever the player
        # isn't currently pressing a movement key. While moving, cycles
        # through all three frames on a timer for a walking effect.
        self.frames, self.flash_frames = _get_frames()
        self.anim_frame_index = 0
        self.anim_timer = 0.0

        # Step 52: souls -- earned by killing enemies (main.py awards
        # them, see settings.SOULS_PER_ENEMY/SOULS_PER_GUARDIAN), spent
        # in the shop that appears once every castle base is cleared.
        # shop_purchases tracks which of settings.SHOP_ITEMS' keys have
        # already been bought -- every item is one-time-only, so this is
        # just a set of the keys bought so far, checked before letting a
        # click do anything (see purchase_shop_item).
        self.souls = 0
        self.shop_purchases = set()

        # Applied as flat multipliers everywhere the base numbers are
        # normally used (handle_movement for speed, main.py's own
        # projectile-damage line for damage, reset_fire_cooldown for
        # attack speed) -- 1.0 (no change) until the matching shop item
        # is bought or a level is gained, both of which multiply these
        # in place (*=) rather than resetting them, so every source of
        # a bonus stacks with every other one already applied.
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.attack_speed_multiplier = 1.0

        # Step 55: leveling -- every kill grants xp (main.py's
        # add_experience calls, right next to the souls award for that
        # same kill). Level 1 is the starting level (no bonus yet); each
        # level gained multiplies speed/damage/attack-speed/max-hp by
        # another +2.5% (see _level_up) and requires more xp than the
        # last one did (see xp_required_for_next_level). Capped at
        # PLAYER_MAX_LEVEL.
        self.level = 1
        self.xp = 0.0

    def handle_movement(self, dt, keys, wall_rects, map_rect=None):
        """Read WASD state and move, sliding along any wall_rects we bump into.

        Movement is accumulated into self.pos (a float Vector2), NOT
        straight into self.rect.x/y. self.rect.x/y can only ever hold
        whole pixels -- assigning a fractional value truncates it away
        every single frame. That truncation always rounds DOWN toward
        negative infinity once the fraction is combined with a large
        positive world coordinate, which meant moving right/down quietly
        lost a bit of speed every frame while moving left/up gained a bit
        -- the "W/A faster than S/D" bug. Keeping the real position in
        self.pos and only rounding it into rect.x/y afterward fixes it:
        all four directions now move at the exact same real speed.
        """
        dx = 0
        dy = 0
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1

        # Move X and Y as two separate steps (rather than one diagonal
        # step), each followed by its own collision check. This is what
        # lets you slide smoothly along a wall when moving into it at an
        # angle, instead of getting fully stopped.
        # Step 52: speed_multiplier is 1.0 (no change) until the shop's
        # "+30% Speed" item is bought -- see Player.__init__.
        self.pos.x += dx * settings.PLAYER_SPEED * self.speed_multiplier * dt
        self.rect.x = round(self.pos.x)
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if dx > 0:
                    self.rect.right = wall_rect.left
                elif dx < 0:
                    self.rect.left = wall_rect.right
                # A wall clamp just moved the rect directly -- pull the
                # float position back in sync, or it'd silently drift
                # into the wall and "remember" it next frame.
                self.pos.x = self.rect.x

        self.pos.y += dy * settings.PLAYER_SPEED * self.speed_multiplier * dt
        self.rect.y = round(self.pos.y)
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if dy > 0:
                    self.rect.bottom = wall_rect.top
                elif dy < 0:
                    self.rect.top = wall_rect.bottom
                self.pos.y = self.rect.y

        # Step 47: clamp to the map's own bounds, same idea as the camera
        # clamp in main.py -- without this, walking off any edge of the
        # map that isn't lined with solid-tagged wall tiles (arena.tmx has
        # none) just kept going forever into the void past the rendered
        # background. map_rect is optional (None skips this) only so old
        # callers/tests that don't pass one don't crash -- every real
        # caller in main.py always passes room.rect.
        if map_rect is not None:
            self.rect.clamp_ip(map_rect)
            self.pos.x = self.rect.x
            self.pos.y = self.rect.y

        # Step 39: advance the walk-cycle while a movement key is
        # actually held, regardless of whether a wall stopped the rect
        # from actually going anywhere -- looks better than freezing mid
        # stride the instant you bump into something. Standing still
        # always snaps back to the neutral frame 0.
        if dx != 0 or dy != 0:
            self.anim_timer -= dt
            if self.anim_timer <= 0:
                self.anim_timer += settings.PLAYER_FRAME_DURATION
                self.anim_frame_index = (self.anim_frame_index + 1) % len(self.frames)
        else:
            self.anim_frame_index = 0
            self.anim_timer = 0.0

    @property
    def equipped_weapon(self):
        return self.weapons[self.weapon_index]

    def handle_weapon_switch(self, keys):
        """Number keys select a weapon directly by slot -- 1 is always the
        first weapon in self.weapons, 2 the second, and so on. Guarded by
        len(self.weapons) so pressing 2 before you've picked up a second
        weapon does nothing instead of crashing."""
        if keys[pygame.K_1] and len(self.weapons) > 0:
            self.weapon_index = 0
        elif keys[pygame.K_2] and len(self.weapons) > 1:
            self.weapon_index = 1

    def add_weapon(self, weapon):
        """Add a weapon to the inventory (skipping it if already carried)
        and immediately switch to it -- called when a WeaponPickup is
        collected."""
        for existing in self.weapons:
            if existing.name == weapon.name:
                return
        self.weapons.append(weapon)
        self.weapon_index = len(self.weapons) - 1

    def xp_required_for_next_level(self):
        """How much banked xp it takes to go from the current level to
        the next one -- grows every level (LEVEL_XP_GROWTH times the
        level before it), so the climb gets steadily longer the higher
        the level. Returns None once already at PLAYER_MAX_LEVEL --
        there's no "next level" left to require anything for, which is
        also how add_experience/hud.py's draw_level_bar know to stop
        showing a progress fraction and just show "MAX" instead."""
        if self.level >= settings.PLAYER_MAX_LEVEL:
            return None
        return round(settings.LEVEL_XP_BASE * (settings.LEVEL_XP_GROWTH ** (self.level - 1)))

    def add_experience(self, amount):
        """Step 55: called by main.py every time a kill lands, right next
        to the matching add_souls call for that same kill. Banks the xp
        and levels up -- possibly more than once, if one big reward (a
        boss kill) covers several levels at once -- as soon as there's
        enough for the next one. A no-op once already at
        PLAYER_MAX_LEVEL, so xp earned past that point is just discarded
        rather than piling up uselessly."""
        if self.level >= settings.PLAYER_MAX_LEVEL:
            return

        self.xp += amount
        xp_required = self.xp_required_for_next_level()
        while xp_required is not None and self.xp >= xp_required:
            self.xp -= xp_required
            self._level_up()
            xp_required = self.xp_required_for_next_level()

    def _level_up(self):
        """+2.5% (settings.LEVEL_ATTRIBUTE_BONUS_PER_LEVEL) to every
        attribute -- speed, damage, attack speed, max health -- applied
        the same "multiply whatever's already there" way
        purchase_shop_item's own buffs are, so this compounds with
        itself across levels AND with any shop items already bought,
        instead of overwriting them. max_health also heals by the exact
        amount the ceiling just went up by, same reasoning as the
        shop's own +Max HP item."""
        self.level += 1
        growth = 1 + settings.LEVEL_ATTRIBUTE_BONUS_PER_LEVEL
        self.speed_multiplier *= growth
        self.damage_multiplier *= growth
        self.attack_speed_multiplier *= growth

        old_max_health = self.max_health
        self.max_health *= growth
        self.health += self.max_health - old_max_health

    def add_souls(self, amount):
        """Step 52: called by main.py every time a projectile kill lands
        (see settings.SOULS_PER_ENEMY/SOULS_PER_GUARDIAN) -- souls are
        the only thing the shop's buttons check against."""
        self.souls += amount

    def purchase_shop_item(self, item):
        """`item` is one of settings.SHOP_ITEMS' own dicts (has "key",
        "name", "cost"). Returns True if the purchase actually went
        through -- False if it was already owned or there aren't enough
        souls, which main.py doesn't need to check itself first, it can
        just call this on every click and let it no-op safely."""
        key = item["key"]
        if key in self.shop_purchases or self.souls < item["cost"]:
            return False

        self.souls -= item["cost"]
        self.shop_purchases.add(key)

        if key == "speed":
            self.speed_multiplier *= settings.SHOP_SPEED_MULTIPLIER
        elif key == "damage":
            self.damage_multiplier *= settings.SHOP_DAMAGE_MULTIPLIER
        elif key == "health":
            # Raises the ceiling AND heals by the same amount the
            # ceiling just went up by -- buying this mid-fight actually
            # restores health instead of just raising a cap you're
            # already far below.
            old_max_health = self.max_health
            self.max_health *= settings.SHOP_HEALTH_MULTIPLIER
            self.health += self.max_health - old_max_health
        elif key == "relic":
            self.add_weapon(_make_relic_weapon())

        return True

    def handle_aim(self, camera_x, camera_y, view_width, view_height, dt=None):
        """Point aim_dir from the player's on-screen position toward the mouse."""
        screen_x = self.rect.centerx - camera_x
        screen_y = self.rect.centery - camera_y

        # pygame.mouse.get_pos() reports real window pixels, but step 22
        # draws the world onto a smaller internal surface (game_surface,
        # view_width x view_height) before stretching it up to fill the
        # window -- so the mouse position has to be scaled down by
        # whatever that stretch factor actually is right now, to land in
        # the same coordinate space as screen_x/screen_y above.
        #
        # Step 51: this used to just divide by settings.ZOOM, which is
        # only true on the castle map -- the arena zooms in FURTHER, to a
        # bigger, runtime-computed factor (see main.py's arena-only zoom,
        # step 49), so dividing by the smaller fixed ZOOM constant there
        # was converting the cursor to the wrong point and aiming off
        # target. Computing the real current factor from the actual
        # screen size vs. view_width/view_height (both passed in by
        # main.py, whichever map is active) instead always matches
        # whatever's really on screen.
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x /= settings.SCREEN_WIDTH / view_width
        mouse_y /= settings.SCREEN_HEIGHT / view_height

        direction = pygame.Vector2(mouse_x - screen_x, mouse_y - screen_y)
        # Guard against the zero-length vector you'd get if the mouse were
        # exactly on top of the player -- normalize() crashes on that.
        if direction.length_squared() > 0:
            target_dir = direction.normalize()
            # Step 65: aim sensitivity (Settings). 100% snaps straight to
            # the cursor; lower values only TURN toward it at a limited
            # speed, so the aim feels smoother/heavier.
            sensitivity = prefs.get_number(
                "aim_sensitivity", settings.AIM_SENSITIVITY_MAX,
                settings.AIM_SENSITIVITY_MIN, settings.AIM_SENSITIVITY_MAX,
            )
            if dt is None or sensitivity >= settings.AIM_SENSITIVITY_MAX - 0.001:
                self.aim_dir = target_dir
            else:
                span = settings.AIM_SENSITIVITY_MAX - settings.AIM_SENSITIVITY_MIN
                t = (sensitivity - settings.AIM_SENSITIVITY_MIN) / span
                rate = settings.AIM_TURN_RATE_AT_MIN + (
                    settings.AIM_TURN_RATE_AT_MAX - settings.AIM_TURN_RATE_AT_MIN
                ) * t
                angle = self.aim_dir.angle_to(target_dir)  # signed, degrees
                angle = (angle + 180) % 360 - 180
                step = max(-rate * dt, min(rate * dt, angle))
                self.aim_dir = self.aim_dir.rotate(step)

    def tick_cooldown(self, dt):
        """Count the fire cooldown down toward 0. Call this once per frame."""
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

    def can_fire(self):
        return self.fire_cooldown <= 0

    def reset_fire_cooldown(self):
        """Call this every time a shot is actually fired. Uses whichever
        weapon is currently equipped, so switching weapons changes the
        rate of fire immediately. Divided by attack_speed_multiplier
        (step 55, >= 1.0) so leveling up shortens the cooldown -- fires
        MORE often -- rather than lengthening it."""
        self.fire_cooldown = self.equipped_weapon.fire_interval / self.attack_speed_multiplier

    def tick_invulnerability(self, dt):
        """Count the invulnerability timer down toward 0. Call this once per frame."""
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

    def take_damage(self, amount):
        """Reduce health by amount, unless currently invulnerable. Returns
        True if this brings health to 0 (used later for the game-over state)."""
        if self.invulnerable_timer > 0:
            return False
        self.health = max(0, self.health - amount)
        self.invulnerable_timer = settings.PLAYER_INVULNERABLE_DURATION
        return self.health <= 0

    def draw(self, screen, camera_x, camera_y):
        screen_center = (self.rect.centerx - camera_x, self.rect.centery - camera_y)

        # Step 39: blink between the normal frame and an all-white copy
        # of it every 0.1s while invulnerable -- the same idea as the old
        # solid-color flash, just done per-sprite instead of per-rect.
        use_flash = self.invulnerable_timer > 0 and int(self.invulnerable_timer * 10) % 2 == 0
        frames = self.flash_frames if use_flash else self.frames
        image = frames[self.anim_frame_index]
        image_rect = image.get_rect(center=screen_center)
        screen.blit(image, image_rect)

        # Step 42: the yellow aim-direction line (a stand-in "gun") is
        # gone now that there's real player art -- it clashed with the
        # sprite. aim_dir itself is untouched, still driving where shots
        # actually fire; this only removes the visual line.