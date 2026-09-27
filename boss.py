"""
Boss: the single enemy waiting in the arena (arena.tmx), fought after
every castle base is cleared and the backstory screen is dismissed.

Deliberately shaped like Enemy (rect/touch_damage/take_damage(amount)/
update(dt, player, wall_rects)/draw(screen, camera_x, camera_y)) so
main.py can drop one straight into room.enemies and every loop that
already knows how to chase-collide/take-projectile-hits/draw "an enemy"
just works, no changes needed there beyond creating it and appending it.
update() returns a freshly-fired Projectile exactly like a guardian's
does (or None) -- main.py's existing enemy_projectiles handling picks
it up unchanged.

Stats (health/damage/speed/attack interval) come from the `difficulty`
dict passed in -- the same one create_game_state() already reads
mines/castle_enemies/map_enemies from (settings.DIFFICULTIES) -- so
Easy's boss is a much smaller threat than Impossible's.

Step 50: once health drops to (or below) BOSS_RAGE_HEALTH_FRACTION of
max_health, the boss enrages -- a ONE-WAY switch for the rest of the
fight. Enraged: bigger (sprite AND hitbox), faster, hits harder (touch
AND projectiles), and fires more often. A red-tinted version of its 4
idle frames plays instead of the normal ones the whole time it's
enraged, so it visibly looks like something just got worse -- no
separate hand-drawn "angry" art needed for that.
"""

import pygame

import settings
from projectile import Projectile


_frames = None              # normal-size, normal-color idle frames
_flash_frames = None        # white silhouette, normal size (hit flash)
_rage_frames = None         # bigger, red-tinted idle frames
_rage_flash_frames = None   # white silhouette, bigger size (hit flash while enraged)


def _remove_checker_background(surface):
    """boss1.1-1.4.png are the same situation as the player/enemy/tower
    art: RGBA but fully opaque (no real transparency), with a light
    gray/white checkerboard baked directly into the pixels instead. Any
    pixel that's both close to gray and bright enough to be checker
    rather than artwork gets turned fully transparent -- see enemy.py's
    own copy of this same function for the fuller explanation."""
    surface = surface.convert_alpha()
    width, height = surface.get_size()
    surface.lock()
    for x in range(width):
        for y in range(height):
            r, g, b, a = surface.get_at((x, y))
            brightness = (r + g + b) / 3
            is_grayish = abs(r - g) <= 8 and abs(g - b) <= 8 and abs(r - b) <= 8
            if is_grayish and brightness >= settings.BOSS_CHECKER_BRIGHTNESS_THRESHOLD:
                surface.set_at((x, y), (r, g, b, 0))
    surface.unlock()
    return surface


def _make_flash_image(image):
    """Same white-silhouette trick as everywhere else in the codebase --
    every visible pixel turned solid white, alpha shape untouched."""
    flash = image.copy()
    width, height = flash.get_size()
    flash.lock()
    for x in range(width):
        for y in range(height):
            r, g, b, a = flash.get_at((x, y))
            if a > 0:
                flash.set_at((x, y), (255, 255, 255, a))
    flash.unlock()
    return flash


def _make_rage_image(image):
    """A red-tinted version of a frame -- every visible pixel blended
    toward settings.BOSS_RAGE_TINT_COLOR by BOSS_RAGE_TINT_BLEND, alpha
    shape untouched. This is what actually plays once the boss enrages,
    instead of a separate hand-drawn "angry" sprite."""
    tinted = image.copy()
    width, height = tinted.get_size()
    tint_r, tint_g, tint_b = settings.BOSS_RAGE_TINT_COLOR
    blend = settings.BOSS_RAGE_TINT_BLEND
    tinted.lock()
    for x in range(width):
        for y in range(height):
            r, g, b, a = tinted.get_at((x, y))
            if a > 0:
                r = round(r + (tint_r - r) * blend)
                g = round(g + (tint_g - g) * blend)
                b = round(b + (tint_b - b) * blend)
                tinted.set_at((x, y), (r, g, b, a))
    tinted.unlock()
    return tinted


def _load_and_clean(path):
    """Load + dekey + crop to content ONCE per source file at full
    resolution -- the expensive per-pixel dekey loop above is the slow
    part, so both the normal-size AND the bigger rage-size frames are
    scaled down from this single cleaned image instead of dekeying the
    same source image twice."""
    image = pygame.image.load(path)
    image = _remove_checker_background(image)
    bounding_rect = image.get_bounding_rect()
    if bounding_rect.width > 0 and bounding_rect.height > 0:
        image = image.subsurface(bounding_rect).copy()
    return image


def _scale_to_height(image, height):
    width, current_height = image.get_size()
    scale = height / current_height
    new_size = (max(1, round(width * scale)), max(1, round(current_height * scale)))
    return pygame.transform.smoothscale(image, new_size)


def _get_frames():
    global _frames, _flash_frames, _rage_frames, _rage_flash_frames
    if _frames is None:
        cleaned = [_load_and_clean(path) for path in settings.BOSS_FRAME_PATHS]

        _frames = [_scale_to_height(image, settings.BOSS_SPRITE_HEIGHT) for image in cleaned]
        _flash_frames = [_make_flash_image(frame) for frame in _frames]

        rage_height = int(settings.BOSS_SPRITE_HEIGHT * settings.BOSS_RAGE_SIZE_MULTIPLIER)
        _rage_frames = [_make_rage_image(_scale_to_height(image, rage_height)) for image in cleaned]
        _rage_flash_frames = [_make_flash_image(frame) for frame in _rage_frames]
    return _frames, _flash_frames, _rage_frames, _rage_flash_frames


class Boss:
    def __init__(self, center, difficulty):
        """`difficulty` is one of settings.DIFFICULTIES' own value dicts
        -- read here for boss_health/boss_damage/boss_speed/
        boss_attack_interval, same idea as create_game_state() already
        reading mines/castle_enemies/map_enemies off it."""
        self.base_speed = difficulty["boss_speed"]
        self.base_damage = difficulty["boss_damage"]
        self.base_attack_interval = difficulty["boss_attack_interval"]

        self.max_health = difficulty["boss_health"]
        self.health = self.max_health
        self.enraged = False  # step 50: one-way, see take_damage/_enrage

        self.rect = pygame.Rect(0, 0, settings.BOSS_SIZE, settings.BOSS_SIZE)
        self.rect.center = center
        # Same reasoning as Player.pos/Enemy.pos -- see Player.handle_movement's
        # own note for why rect.x/y alone loses fractional movement.
        self.pos = pygame.Vector2(self.rect.topleft)

        self.fire_cooldown = 0.0
        self.hit_flash_timer = 0.0

        self.frames, self.flash_frames, self.rage_frames, self.rage_flash_frames = _get_frames()
        self.anim_frame_index = 0
        self.anim_timer = settings.BOSS_FRAME_DURATION

    @property
    def touch_damage(self):
        """Read by main.py exactly like Enemy.touch_damage -- the amount
        the player takes just from colliding with the boss."""
        if self.enraged:
            return self.base_damage * settings.BOSS_RAGE_DAMAGE_MULTIPLIER
        return self.base_damage

    def take_damage(self, amount):
        """Same interface as Enemy.take_damage -- main.py's projectile-
        hit loop calls this identically whether it just hit a regular
        enemy, a guardian, or the boss. Checks the rage threshold every
        time health actually drops, since that's the only thing that
        can trigger it."""
        self.health -= amount
        self.hit_flash_timer = settings.ENEMY_HIT_FLASH_DURATION
        if not self.enraged and self.health <= self.max_health * settings.BOSS_RAGE_HEALTH_FRACTION:
            self._enrage()
        return self.health <= 0

    def _enrage(self):
        """One-way switch -- once triggered, stays enraged for the rest
        of the fight (there's no healing mechanic to ever bring it back
        above the threshold anyway). Grows the hitbox to match the
        bigger rage sprite, right around its current center."""
        self.enraged = True
        width_increase = round(self.rect.width * (settings.BOSS_RAGE_SIZE_MULTIPLIER - 1))
        height_increase = round(self.rect.height * (settings.BOSS_RAGE_SIZE_MULTIPLIER - 1))
        self.rect.inflate_ip(width_increase, height_increase)
        self.pos = pygame.Vector2(self.rect.topleft)

    def update(self, dt, player, wall_rects):
        """Always chases -- no AGGRO_RADIUS gate like a regular Enemy,
        since this is a dedicated boss room and there's nowhere else for
        the player to be. May also fire a projectile straight at the
        player, returned the same way a guardian's shot is (see
        enemy.py's own Enemy.update) so main.py's existing
        enemy_projectiles handling needs no changes to pick it up."""
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        self.anim_timer -= dt
        if self.anim_timer <= 0:
            self.anim_timer += settings.BOSS_FRAME_DURATION
            self.anim_frame_index = (self.anim_frame_index + 1) % len(self.frames)

        speed = self.base_speed * settings.BOSS_RAGE_SPEED_MULTIPLIER if self.enraged else self.base_speed

        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.pos.x += direction.x * speed * dt
        self.rect.x = round(self.pos.x)
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if direction.x > 0:
                    self.rect.right = wall_rect.left
                elif direction.x < 0:
                    self.rect.left = wall_rect.right
                self.pos.x = self.rect.x

        self.pos.y += direction.y * speed * dt
        self.rect.y = round(self.pos.y)
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if direction.y > 0:
                    self.rect.bottom = wall_rect.top
                elif direction.y < 0:
                    self.rect.top = wall_rect.bottom
                self.pos.y = self.rect.y

        return self._shoot(direction, dt, player)

    def _shoot(self, direction_to_player, dt, player):
        """Fires straight at the player once they're within
        BOSS_SHOOT_RANGE, at most once every (possibly rage-shortened)
        attack interval. Returns the new Projectile, or None."""
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

        attack_interval = self.base_attack_interval
        if self.enraged:
            attack_interval *= settings.BOSS_RAGE_ATTACK_INTERVAL_MULTIPLIER

        distance = pygame.Vector2(player.rect.center).distance_to(self.rect.center)
        if distance > settings.BOSS_SHOOT_RANGE or self.fire_cooldown > 0:
            return None

        self.fire_cooldown = attack_interval
        damage = self.base_damage * settings.BOSS_RAGE_DAMAGE_MULTIPLIER if self.enraged else self.base_damage
        return Projectile(self.rect.center, direction_to_player, settings.BOSS_PROJECTILE_SPEED, damage)

    def draw(self, screen, camera_x, camera_y):
        screen_center = (self.rect.centerx - camera_x, self.rect.centery - camera_y)
        flashing = self.hit_flash_timer > 0

        if self.enraged:
            frames = self.rage_flash_frames if flashing else self.rage_frames
        else:
            frames = self.flash_frames if flashing else self.frames

        image = frames[self.anim_frame_index]
        image_rect = image.get_rect(center=screen_center)
        screen.blit(image, image_rect)
