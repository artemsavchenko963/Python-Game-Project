"""
Enemy: health, movement/shooting behavior, and (step 45) real sprite art
for the thing that used to be a colored square.

Step 26a: two flavors now exist, both built from this one class:

- Regular enemies (is_guardian=False): chase the player, but only once
  the player gets within settings.AGGRO_RADIUS -- outside that range
  they just stand still. This is what lets you approach a base
  carefully instead of every enemy on the map swarming you at once.
- Base guardians (is_guardian=True): bigger, far tankier, hit harder,
  and NEVER move at all -- being stationary is what makes a "base" feel
  like an actual structure to storm rather than just another wandering
  monster.

Movement (for non-guardians) uses the same axis-separated wall-collision
technique as Player.handle_movement -- worth comparing the two side by
side.

Step 27: guardians now shoot. update() returns None most frames, but for
a guardian that just fired, it returns a brand new Projectile -- main.py
is what actually appends that into its own enemy_projectiles list and
moves/collides it each frame, same division of responsibility as the
player's own projectiles (Enemy/Player never own a projectile list
themselves, main.py does).

Step 45: regular enemies cycle a slow 2-frame idle "wiggle"
(enemy.png/enemy2.png). Guardians show tower.png normally, switching to
tower2.png (a muzzle-flash pose) for a moment right after they fire.
Both kinds flash a white silhouette version of whatever frame they're
currently showing for ENEMY_HIT_FLASH_DURATION when they take damage
(same idea as Player's invulnerability flash) instead of the old flat
color swap.
"""

import pygame

import settings
from projectile import Projectile


_enemy_frames = None       # [enemy.png, enemy2.png], cleaned + scaled
_enemy_flash_frames = None  # white-silhouette versions of the above
_guardian_images = None     # {"normal": tower.png, "shoot": tower2.png}, cleaned + scaled
_guardian_flash_images = None


def _remove_checker_background(surface):
    """These PNGs are fully opaque (no real alpha channel) -- the
    background is a light gray/white checkerboard baked into the pixels
    instead. Same approach as player.py/mine.py/projectile.py: any pixel
    that's both close to gray and bright enough to be checker rather
    than artwork gets turned fully transparent."""
    surface = surface.convert_alpha()
    width, height = surface.get_size()
    surface.lock()
    for x in range(width):
        for y in range(height):
            r, g, b, a = surface.get_at((x, y))
            brightness = (r + g + b) / 3
            is_grayish = abs(r - g) <= 8 and abs(g - b) <= 8 and abs(r - b) <= 8
            if is_grayish and brightness >= settings.ENEMY_SPRITE_CHECKER_BRIGHTNESS_THRESHOLD:
                surface.set_at((x, y), (r, g, b, 0))
    surface.unlock()
    return surface


def _make_flash_image(image):
    """A white silhouette of an image (every visible pixel turned white,
    same alpha shape) -- shown instead of the normal art while
    hit_flash_timer is running."""
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


def _load_square_frame(path, size):
    image = pygame.image.load(path)
    image = _remove_checker_background(image)
    bounding_rect = image.get_bounding_rect()
    if bounding_rect.width > 0 and bounding_rect.height > 0:
        image = image.subsurface(bounding_rect).copy()
    return pygame.transform.smoothscale(image, (size, size))


def _load_height_scaled(path, height):
    image = pygame.image.load(path)
    image = _remove_checker_background(image)
    bounding_rect = image.get_bounding_rect()
    if bounding_rect.width > 0 and bounding_rect.height > 0:
        image = image.subsurface(bounding_rect).copy()
    width, current_height = image.get_size()
    scale = height / current_height
    new_size = (max(1, round(width * scale)), max(1, round(current_height * scale)))
    return pygame.transform.smoothscale(image, new_size)


def _get_enemy_frames():
    global _enemy_frames, _enemy_flash_frames
    if _enemy_frames is None:
        _enemy_frames = [
            _load_square_frame(path, settings.ENEMY_SPRITE_SIZE) for path in settings.ENEMY_FRAME_PATHS
        ]
        _enemy_flash_frames = [_make_flash_image(frame) for frame in _enemy_frames]
    return _enemy_frames, _enemy_flash_frames


def _get_guardian_images():
    global _guardian_images, _guardian_flash_images
    if _guardian_images is None:
        _guardian_images = {
            "normal": _load_height_scaled(settings.GUARDIAN_IMAGE_PATH, settings.GUARDIAN_SPRITE_HEIGHT),
            "shoot": _load_height_scaled(settings.GUARDIAN_SHOOT_IMAGE_PATH, settings.GUARDIAN_SPRITE_HEIGHT),
        }
        _guardian_flash_images = {
            key: _make_flash_image(image) for key, image in _guardian_images.items()
        }
    return _guardian_images, _guardian_flash_images


class Enemy:
    def __init__(self, center, is_guardian=False):
        self.is_guardian = is_guardian

        size = settings.GUARDIAN_SIZE if is_guardian else settings.ENEMY_SIZE
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = center

        # Same reasoning as Player.pos -- see the note in
        # Player.handle_movement for why rect.x/y alone isn't enough.
        self.pos = pygame.Vector2(self.rect.topleft)

        self.max_health = settings.GUARDIAN_MAX_HEALTH if is_guardian else settings.ENEMY_MAX_HEALTH
        self.health = self.max_health

        # Read once here instead of main.py using one fixed constant for
        # every enemy -- a guardian hits noticeably harder than a regular
        # one on touch.
        self.touch_damage = settings.GUARDIAN_TOUCH_DAMAGE if is_guardian else settings.ENEMY_TOUCH_DAMAGE

        # Only ever used by guardians (step 27) -- counts down to 0,
        # same shape as Player.fire_cooldown. Starts at 0 so a guardian's
        # first shot isn't delayed.
        self.fire_cooldown = 0.0

        # Step 43: counts down to 0; while above 0, draw() shows a white
        # silhouette instead of the normal art -- a quick "you just got
        # hit" flash, reset every time take_damage() actually lands.
        self.hit_flash_timer = 0.0

        if is_guardian:
            self.images, self.flash_images = _get_guardian_images()
            # Step 45: counts down to 0; while above 0, draw() shows the
            # tower2 (muzzle-flash) pose instead of the resting one --
            # set every time _guardian_shoot actually fires.
            self.shoot_flash_timer = 0.0
        else:
            self.frames, self.flash_frames = _get_enemy_frames()
            self.anim_frame_index = 0
            self.anim_timer = settings.ENEMY_FRAME_DURATION

    def take_damage(self, amount):
        """Reduce health by amount. Returns True if this kills the enemy."""
        self.health -= amount
        self.hit_flash_timer = settings.ENEMY_HIT_FLASH_DURATION
        return self.health <= 0

    def update(self, dt, player, wall_rects):
        """Move straight toward the player, colliding with walls like the
        player does -- unless this is a guardian (never moves, full
        stop, but may fire instead -- see _guardian_shoot), or the
        player is still outside AGGRO_RADIUS (stands still until
        approached).

        Returns None most of the time. The one exception: a guardian
        that just fired returns a brand new Projectile aimed at the
        player -- main.py is responsible for actually tracking/moving/
        drawing it from there, same as it already does for the player's
        own projectiles.
        """
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        if self.is_guardian:
            if self.shoot_flash_timer > 0:
                self.shoot_flash_timer -= dt
            projectile = self._guardian_shoot(dt, player)
            if projectile is not None:
                self.shoot_flash_timer = settings.GUARDIAN_SHOOT_FLASH_DURATION
            return projectile

        # Step 45: the idle wiggle cycles on its own clock regardless of
        # whether this enemy is currently chasing -- there's no separate
        # walk/idle pose in this art, just two tentacle positions.
        self.anim_timer -= dt
        if self.anim_timer <= 0:
            self.anim_timer += settings.ENEMY_FRAME_DURATION
            self.anim_frame_index = (self.anim_frame_index + 1) % len(self.frames)

        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        distance = direction.length()
        if distance > settings.AGGRO_RADIUS:
            return None
        if distance > 0:
            direction = direction.normalize()

        self.pos.x += direction.x * settings.ENEMY_SPEED * dt
        self.rect.x = round(self.pos.x)
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if direction.x > 0:
                    self.rect.right = wall_rect.left
                elif direction.x < 0:
                    self.rect.left = wall_rect.right
                self.pos.x = self.rect.x

        self.pos.y += direction.y * settings.ENEMY_SPEED * dt
        self.rect.y = round(self.pos.y)
        for wall_rect in wall_rects:
            if self.rect.colliderect(wall_rect):
                if direction.y > 0:
                    self.rect.bottom = wall_rect.top
                elif direction.y < 0:
                    self.rect.top = wall_rect.bottom
                self.pos.y = self.rect.y

        return None

    def _guardian_shoot(self, dt, player):
        """Guardians never move, but periodically fire a projectile
        straight at the player once they're within GUARDIAN_SHOOT_RANGE.
        Returns the new Projectile, or None if it's not time to fire yet
        (or the player is out of range)."""
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

        direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        distance = direction.length()
        if distance > settings.GUARDIAN_SHOOT_RANGE or self.fire_cooldown > 0:
            return None

        self.fire_cooldown = settings.GUARDIAN_FIRE_INTERVAL
        if distance > 0:
            direction = direction.normalize()
        return Projectile(
            self.rect.center, direction, settings.GUARDIAN_PROJECTILE_SPEED, settings.GUARDIAN_PROJECTILE_DAMAGE
        )

    def draw(self, screen, camera_x, camera_y):
        screen_center = (self.rect.centerx - camera_x, self.rect.centery - camera_y)
        flashing = self.hit_flash_timer > 0

        if self.is_guardian:
            pose = "shoot" if self.shoot_flash_timer > 0 else "normal"
            image = self.flash_images[pose] if flashing else self.images[pose]
        else:
            image = (self.flash_frames if flashing else self.frames)[self.anim_frame_index]

        image_rect = image.get_rect(center=screen_center)
        screen.blit(image, image_rect)