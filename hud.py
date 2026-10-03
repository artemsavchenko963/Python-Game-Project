"""
HUD (heads-up display): draws on-screen UI that isn't part of the game
world -- starting with the player's health bar in the top-left corner.

This is the first thing we've drawn that does NOT subtract the camera.
Everything else so far (player, room, enemies, projectiles) lives in
world coordinates and needs world_position - camera to land in the right
screen spot. The health bar has no world position at all -- it's always
"20 pixels from the corner of the window," full stop -- so it's drawn
directly in screen coordinates.
"""

import pygame

import i18n
import settings


def get_hud_panel_rect(screen):
    """Where the left-side HUD backdrop panel sits -- big enough to
    contain the health bar plus the three text rows below it, with
    HUD_PANEL_PADDING of breathing room on every side. A separate
    function (same reasoning as every other "where does this sit"
    helper in this file) even though nothing outside draw_hud_panel
    needs it yet."""
    padding = settings.HUD_PANEL_PADDING
    gap = settings.HUD_PANEL_ROW_GAP
    content_height = (
        settings.HEALTH_BAR_HEIGHT
        + gap + settings.BASES_LABEL_FONT_SIZE
        + gap + settings.SCANNER_LABEL_FONT_SIZE
    )
    x = settings.HUD_MARGIN - padding
    y = settings.HUD_MARGIN - padding
    width = settings.HUD_PANEL_WIDTH
    height = content_height + padding * 2
    return pygame.Rect(x, y, width, height)


def draw_hud_panel(screen):
    """Step 54: a single rounded, red-tinted backdrop drawn BEHIND the
    whole left-side stack (health bar, bases label, scanner label) --
    before this they were just plain text floating directly over the
    game world, which read as "looks bad" next to the shop panel/souls
    badge's own rounded style. main.py calls this FIRST, before
    draw_health_bar/draw_bases_label/draw_scanner_label -- none of those
    changed their own x/y math at all, they just end up sitting visually
    on top of this panel now."""
    rect = get_hud_panel_rect(screen)
    panel_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(
        panel_surface, settings.HUD_PANEL_BG_COLOR, panel_surface.get_rect(),
        border_radius=settings.HUD_PANEL_BORDER_RADIUS,
    )
    screen.blit(panel_surface, rect.topleft)
    pygame.draw.rect(screen, settings.HUD_PANEL_BORDER_COLOR, rect, 2, border_radius=settings.HUD_PANEL_BORDER_RADIUS)


def draw_level_bar(screen, player):
    """Step 60: the XP/level strip now lives in the top-left panel slot
    the health bar used to have (the two swapped places). Drawn on
    game_surface like the rest of that panel. Fills as kills feed
    Player.add_experience toward the next level; reads "MAX" once
    PLAYER_MAX_LEVEL is reached (xp_required_for_next_level() is None)."""
    x = settings.HUD_MARGIN
    y = settings.HUD_MARGIN
    width = settings.HEALTH_BAR_WIDTH
    height = settings.HEALTH_BAR_HEIGHT
    radius = settings.HEALTH_BAR_BORDER_RADIUS

    background_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, settings.HEALTH_BAR_BG_COLOR, background_rect, border_radius=radius)

    xp_required = player.xp_required_for_next_level()
    if xp_required is not None and xp_required > 0:
        fraction = max(0.0, min(1.0, player.xp / xp_required))
        fill_width = int(width * fraction)
        if fill_width > 0:
            pygame.draw.rect(
                screen, settings.LEVEL_BAR_FILL_COLOR, pygame.Rect(x, y, fill_width, height),
                border_radius=radius,
            )
    pygame.draw.rect(
        screen, settings.HEALTH_BAR_BORDER_COLOR, background_rect,
        settings.HEALTH_BAR_BORDER_WIDTH, border_radius=radius,
    )

    font = pygame.font.SysFont(None, settings.LEVEL_PANEL_LABEL_FONT_SIZE, bold=True)
    if xp_required is None:
        text = f"{i18n.t('level_short')} {player.level}  ({i18n.t('max')})"
        color = settings.LEVEL_BAR_MAX_COLOR
    else:
        text = f"{i18n.t('level_short')} {player.level}   {int(player.xp)}/{xp_required}"
        color = settings.LEVEL_BAR_LABEL_COLOR
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, text_surface.get_rect(center=background_rect.center))


def draw_bases_label(screen, bases_remaining, total_bases):
    """Step 26d (relabeled step 58): shows how many towers are still
    standing, just below the health bar. A base now counts as
    "remaining" purely by whether its own guardian (tower) is alive --
    its scattered minions don't factor in at all anymore."""
    font = pygame.font.SysFont(None, settings.BASES_LABEL_FONT_SIZE, bold=True)
    text = i18n.t("towers", remaining=bases_remaining, total=total_bases)
    surface = font.render(text, True, settings.HUD_TEXT_COLOR)
    x = settings.HUD_MARGIN
    y = settings.HUD_MARGIN + settings.HEALTH_BAR_HEIGHT + settings.ui(8)
    screen.blit(surface, (x, y))


def draw_scanner_label(screen, scanner_cooldown):
    """Step 35: shows whether E (scan) is ready or still on cooldown,
    just below the bases label -- without this there'd be no way to
    tell "can I scan again yet" other than pressing E and seeing nothing
    happen."""
    font = pygame.font.SysFont(None, settings.SCANNER_LABEL_FONT_SIZE, bold=True)
    if scanner_cooldown <= 0:
        text = i18n.t("scanner_ready")
    else:
        text = i18n.t("scanner_cooldown", seconds=f"{scanner_cooldown:.1f}")
    surface = font.render(text, True, settings.HUD_TEXT_COLOR)
    x = settings.HUD_MARGIN
    y = (
        settings.HUD_MARGIN
        + settings.HEALTH_BAR_HEIGHT
        + 8
        + settings.BASES_LABEL_FONT_SIZE
        + 8
    )
    screen.blit(surface, (x, y))


def _draw_soul_orb(screen, center, radius, glow=True):
    """The little glowing icon that stands in for a currency icon,
    everywhere souls show up (the top-center badge, and each shop item's
    cost) -- drawn as plain shapes rather than an emoji/image file so it
    always renders crisply at any size. `glow` is turned off for the
    small per-item icons in the shop list (a soft halo reads fine big,
    just looks like a smudge at 6px radius) -- the big top-center badge
    is the only place the halo is worth it."""
    if glow:
        halo_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        halo_center = (radius * 2, radius * 2)
        pygame.draw.circle(halo_surface, (*settings.SOULS_ICON_COLOR, 55), halo_center, radius * 2)
        pygame.draw.circle(halo_surface, (*settings.SOULS_ICON_COLOR, 110), halo_center, int(radius * 1.4))
        screen.blit(halo_surface, (center[0] - radius * 2, center[1] - radius * 2))

    pygame.draw.circle(screen, settings.SOULS_ICON_COLOR, center, radius)
    pygame.draw.circle(screen, settings.SOULS_ICON_CORE_COLOR, center, max(1, radius // 2))


def get_souls_badge_rect(screen):
    """Where the souls badge sits -- top-center of the real window. A
    FIXED size (settings.SOULS_BADGE_WIDTH/HEIGHT), not measured from the
    current souls text, so the badge never subtly resizes as the number
    grows -- same reasoning as get_pause_button_rect being its own
    function: main.py doesn't need this one today, but draw_souls_badge
    below does, and keeping it separate matches every other "where does
    this HUD element sit" helper in this file."""
    width = settings.SOULS_BADGE_WIDTH
    height = settings.SOULS_BADGE_HEIGHT
    x = screen.get_width() // 2 - width // 2
    y = settings.SOULS_BADGE_TOP_MARGIN
    return pygame.Rect(x, y, width, height)


def draw_souls_badge(screen, player):
    """Step 53: the player's current souls, as a rounded pill badge
    top-center of the screen -- moved out of the left-side health/
    weapon/bases/scanner stack (step 52's first attempt) since a
    currency counter reads better as its own persistent element than as
    just another line of text in that stack."""
    rect = get_souls_badge_rect(screen)
    radius = rect.height // 2

    badge_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(badge_surface, settings.SOULS_BADGE_BG_COLOR, badge_surface.get_rect(), border_radius=radius)
    screen.blit(badge_surface, rect.topleft)
    pygame.draw.rect(screen, settings.SOULS_BADGE_BORDER_COLOR, rect, 2, border_radius=radius)

    icon_radius = settings.SOULS_ICON_RADIUS
    icon_center = (rect.x + settings.ui(16) + icon_radius, rect.centery)
    _draw_soul_orb(screen, icon_center, icon_radius)

    font = pygame.font.SysFont(None, settings.SOULS_BADGE_FONT_SIZE, bold=True)
    text_surface = font.render(str(player.souls), True, settings.SOULS_BADGE_TEXT_COLOR)
    text_rect = text_surface.get_rect(midleft=(icon_center[0] + icon_radius + settings.ui(10), rect.centery))
    screen.blit(text_surface, text_rect)


def get_health_bar_rect(screen):
    """Where the player's health bar sits -- bottom-center of the real
    window (step 60: swapped with the level bar, which took over the
    old top-left health bar slot)."""
    width = settings.LEVEL_BAR_WIDTH
    height = settings.LEVEL_BAR_HEIGHT
    x = screen.get_width() // 2 - width // 2
    y = screen.get_height() - settings.LEVEL_BAR_BOTTOM_MARGIN - height
    return pygame.Rect(x, y, width, height)


def draw_health_bar(screen, player):
    """Step 60: the player's health bar, bottom-center of the real
    screen (crisp, fixed size regardless of zoom), with an "HP cur/max"
    label."""
    rect = get_health_bar_rect(screen)
    radius = settings.LEVEL_BAR_BORDER_RADIUS

    bg_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, settings.LEVEL_BAR_BG_COLOR, bg_surface.get_rect(), border_radius=radius)
    screen.blit(bg_surface, rect.topleft)

    fraction = max(0.0, min(1.0, player.health / player.max_health)) if player.max_health > 0 else 0.0
    fill_width = round(rect.width * fraction)
    if fill_width > 0:
        fill_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            fill_surface, settings.HEALTH_BAR_FILL_COLOR, pygame.Rect(0, 0, fill_width, rect.height),
            border_radius=radius,
        )
        screen.blit(fill_surface, rect.topleft)

    pygame.draw.rect(
        screen, settings.LEVEL_BAR_BORDER_COLOR, rect,
        settings.LEVEL_BAR_BORDER_WIDTH, border_radius=radius,
    )

    font = pygame.font.SysFont(None, settings.LEVEL_BAR_LABEL_FONT_SIZE, bold=True)
    text = f"{i18n.t('hp')}  {int(round(player.health))}/{int(round(player.max_health))}"
    text_surface = font.render(text, True, settings.LEVEL_BAR_LABEL_COLOR)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))


def draw_boss_fight_prompt(screen):
    """Step 47: shown once every base is cleared, instead of teleporting
    into the arena map right away -- lets the player finish looting/
    exploring the castle first and walk into the boss fight on their own
    terms by pressing E. A dark box behind the text keeps it readable
    over any part of the map/fog it happens to sit on top of."""
    font = pygame.font.SysFont(None, settings.BOSS_FIGHT_PROMPT_FONT_SIZE)
    text_surface = font.render(i18n.t("boss_prompt"), True, settings.BOSS_FIGHT_PROMPT_TEXT_COLOR)

    padding = settings.BOSS_FIGHT_PROMPT_PADDING
    box_width = text_surface.get_width() + padding * 2
    box_height = text_surface.get_height() + padding * 2
    box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    box.fill((*settings.BOSS_FIGHT_PROMPT_BG_COLOR, settings.BOSS_FIGHT_PROMPT_BG_ALPHA))

    box_rect = box.get_rect(midtop=(screen.get_width() // 2, settings.BOSS_FIGHT_PROMPT_TOP_MARGIN))
    screen.blit(box, box_rect)
    pygame.draw.rect(screen, settings.HEALTH_BAR_BORDER_COLOR, box_rect, 2)

    text_rect = text_surface.get_rect(center=box_rect.center)
    screen.blit(text_surface, text_rect)


def draw_tower_intro_prompt(screen, tower_count, timer):
    """Step 58: a one-time hint shown for the first few seconds of a
    castle run -- tells the player the shop/boss fight unlock once every
    TOWER (guardian) is dead, not every scattered minion, which is easy
    to assume otherwise now that minions are purely optional loot/xp.
    `timer` counts down from settings.TOWER_INTRO_PROMPT_DURATION
    (main.py's own tower_prompt_timer, only ticking while the game is
    actually running -- not paused, not game over, not already won).
    Draws nothing once timer reaches 0, and eases its own alpha down to
    0 over the last TOWER_INTRO_PROMPT_FADE_DURATION seconds instead of
    just vanishing abruptly."""
    if timer <= 0 or tower_count <= 0:
        return

    fade_duration = settings.TOWER_INTRO_PROMPT_FADE_DURATION
    alpha_fraction = min(1.0, timer / fade_duration) if fade_duration > 0 else 1.0

    text = i18n.t("tower_intro", count=tower_count)
    font = pygame.font.SysFont(None, settings.TOWER_INTRO_PROMPT_FONT_SIZE, bold=True)
    text_surface = font.render(text, True, settings.TOWER_INTRO_PROMPT_TEXT_COLOR)

    padding = settings.TOWER_INTRO_PROMPT_PADDING
    box_width = text_surface.get_width() + padding * 2
    box_height = text_surface.get_height() + padding * 2
    radius = 12

    box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    bg_alpha = round(settings.TOWER_INTRO_PROMPT_BG_ALPHA * alpha_fraction)
    pygame.draw.rect(box, (*settings.TOWER_INTRO_PROMPT_BG_COLOR, bg_alpha), box.get_rect(), border_radius=radius)

    border_alpha = round(255 * alpha_fraction)
    pygame.draw.rect(
        box, (*settings.TOWER_INTRO_PROMPT_BORDER_COLOR, border_alpha), box.get_rect(),
        2, border_radius=radius,
    )

    box_rect = box.get_rect(midtop=(screen.get_width() // 2, settings.TOWER_INTRO_PROMPT_TOP_MARGIN))
    screen.blit(box, box_rect)

    text_surface.set_alpha(round(255 * alpha_fraction))
    text_rect = text_surface.get_rect(center=box_rect.center)
    screen.blit(text_surface, text_rect)


def get_boss_health_bar_rect(screen):
    """Where the boss health bar sits, in real window coordinates --
    top-center, just below the souls badge. A separate function, same
    reasoning as every other "where does this sit" helper in this file."""
    width = settings.BOSS_HEALTH_BAR_WIDTH
    height = settings.BOSS_HEALTH_BAR_HEIGHT
    x = screen.get_width() // 2 - width // 2
    y = settings.BOSS_HEALTH_BAR_TOP_MARGIN
    return pygame.Rect(x, y, width, height)


def draw_boss_health_bar(screen, boss):
    """Step 54: a boss-fight-style health bar, top-center, shown only
    while in_arena -- main.py finds the current Boss instance in
    room.enemies each frame (the same way it already checks for
    isinstance(..., Boss) elsewhere) and passes it straight in here,
    rather than boss.py or main.py needing a whole new tracked variable.
    Drawn on the real screen (like the souls badge/shop panel), not
    game_surface, so it stays a fixed, crisp size no matter the arena's
    own zoom. Turns orange with an "ENRAGED" label once the boss crosses
    BOSS_RAGE_HEALTH_FRACTION -- the same one-way switch that makes it
    bigger/faster/harder-hitting."""
    rect = get_boss_health_bar_rect(screen)
    radius = settings.BOSS_HEALTH_BAR_BORDER_RADIUS

    bg_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, settings.BOSS_HEALTH_BAR_BG_COLOR, bg_surface.get_rect(), border_radius=radius)
    screen.blit(bg_surface, rect.topleft)

    fraction = 0.0
    if boss.max_health > 0:
        fraction = max(0.0, min(1.0, boss.health / boss.max_health))
    fill_color = settings.BOSS_HEALTH_BAR_ENRAGED_FILL_COLOR if boss.enraged else settings.BOSS_HEALTH_BAR_FILL_COLOR
    fill_width = round(rect.width * fraction)
    if fill_width > 0:
        fill_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(fill_surface, fill_color, pygame.Rect(0, 0, fill_width, rect.height), border_radius=radius)
        screen.blit(fill_surface, rect.topleft)

    pygame.draw.rect(
        screen, settings.BOSS_HEALTH_BAR_BORDER_COLOR, rect,
        settings.BOSS_HEALTH_BAR_BORDER_WIDTH, border_radius=radius,
    )

    label_font = pygame.font.SysFont(None, settings.BOSS_HEALTH_BAR_LABEL_FONT_SIZE, bold=True)
    if boss.enraged:
        label_text = i18n.t("boss_rage")
        label_color = settings.BOSS_HEALTH_BAR_RAGE_LABEL_COLOR
    else:
        label_text = i18n.t("boss_label")
        label_color = settings.BOSS_HEALTH_BAR_LABEL_COLOR
    label_surface = label_font.render(label_text, True, label_color)
    label_rect = label_surface.get_rect(midbottom=(rect.centerx, rect.top - settings.ui(4)))
    screen.blit(label_surface, label_rect)


def get_shop_panel_rect(screen):
    """Where the shop panel sits, in real window coordinates -- bottom-
    right corner, same "drawn directly on the real window" reasoning as
    the pause button (get_pause_button_rect): stays a fixed, crisp size
    and clickable position no matter what zoom is active on either map.
    A separate function (rather than computing this inline in
    draw_shop) so main.py's click handling and get_shop_button_rects
    below can both use the exact same math."""
    width = settings.SHOP_PANEL_WIDTH
    padding = settings.SHOP_PANEL_PADDING
    title_row_height = settings.SHOP_TITLE_FONT_SIZE + 10
    items = settings.SHOP_ITEMS
    item_height = settings.SHOP_ITEM_HEIGHT
    gap = settings.SHOP_ITEM_GAP

    content_height = title_row_height + len(items) * item_height + max(0, len(items) - 1) * gap
    height = padding * 2 + content_height

    x = screen.get_width() - settings.SHOP_PANEL_MARGIN - width
    y = screen.get_height() - settings.SHOP_PANEL_MARGIN - height
    return pygame.Rect(x, y, width, height)


def get_shop_button_rects(screen):
    """One (item, rect) pair per settings.SHOP_ITEMS entry, stacked
    inside the shop panel -- real window coordinates, same reasoning as
    get_shop_panel_rect. main.py uses this exact list both to test
    clicks against and (indirectly, via draw_shop) to know where each
    button actually is."""
    panel_rect = get_shop_panel_rect(screen)
    padding = settings.SHOP_PANEL_PADDING
    title_row_height = settings.SHOP_TITLE_FONT_SIZE + 10
    item_height = settings.SHOP_ITEM_HEIGHT
    gap = settings.SHOP_ITEM_GAP

    rects = []
    y = panel_rect.y + padding + title_row_height
    for item in settings.SHOP_ITEMS:
        rect = pygame.Rect(panel_rect.x + padding, y, panel_rect.width - padding * 2, item_height)
        rects.append((item, rect))
        y += item_height + gap
    return rects


def draw_shop(screen, player):
    """Step 52, redesigned step 53: the shop panel itself -- pops up in
    the bottom-right corner once every castle base is cleared (main.py
    gates the call on the same bases_cleared/not in_arena condition the
    boss-fight prompt already uses), so there's a chance to spend souls
    before walking into the arena.

    Each button: a colored accent bar on the left (settings.
    SHOP_ITEM_COLORS, just so the four items are easy to tell apart at a
    glance), the item's name, and its cost with a small soul-orb icon --
    or, once bought, the whole button turns green and just says "Owned".
    Rounded corners throughout instead of the old sharp-edged boxes."""
    panel_rect = get_shop_panel_rect(screen)
    panel_radius = settings.SHOP_PANEL_BORDER_RADIUS

    panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, settings.SHOP_PANEL_BG_COLOR, panel_surface.get_rect(), border_radius=panel_radius)
    screen.blit(panel_surface, panel_rect.topleft)
    pygame.draw.rect(screen, settings.SHOP_PANEL_BORDER_COLOR, panel_rect, 2, border_radius=panel_radius)

    padding = settings.SHOP_PANEL_PADDING
    title_font = pygame.font.SysFont(None, settings.SHOP_TITLE_FONT_SIZE, bold=True)
    title_surface = title_font.render(i18n.t("shop_title"), True, settings.SHOP_TITLE_COLOR)
    title_pos = (panel_rect.x + padding, panel_rect.y + padding - settings.ui(2))
    screen.blit(title_surface, title_pos)

    divider_y = title_pos[1] + title_surface.get_height() + settings.ui(6)
    pygame.draw.line(
        screen, settings.SHOP_DIVIDER_COLOR,
        (panel_rect.x + padding, divider_y),
        (panel_rect.right - padding, divider_y),
        2,
    )

    name_font = pygame.font.SysFont(None, settings.SHOP_ITEM_FONT_SIZE, bold=True)
    cost_font = pygame.font.SysFont(None, max(settings.UI_MIN_FONT_SIZE, settings.SHOP_ITEM_FONT_SIZE - 1))
    button_radius = settings.SHOP_BUTTON_BORDER_RADIUS
    accent_width = settings.SHOP_BUTTON_ACCENT_WIDTH
    mouse_pos = pygame.mouse.get_pos()

    for item, rect in get_shop_button_rects(screen):
        purchased = item["key"] in player.shop_purchases
        can_afford = player.souls >= item["cost"]

        if purchased:
            bg_color = settings.SHOP_BUTTON_PURCHASED_COLOR
        elif not can_afford:
            bg_color = settings.SHOP_BUTTON_DISABLED_COLOR
        elif rect.collidepoint(mouse_pos):
            bg_color = settings.SHOP_BUTTON_HOVER_COLOR
        else:
            bg_color = settings.SHOP_BUTTON_COLOR

        button_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        button_local_rect = button_surface.get_rect()
        pygame.draw.rect(button_surface, bg_color, button_local_rect, border_radius=button_radius)
        # A faint lighter band across the top half -- just enough of a
        # glossy highlight that the button reads as a raised, clickable
        # surface rather than a flat rectangle.
        highlight_rect = pygame.Rect(0, 0, rect.width, rect.height // 2)
        pygame.draw.rect(button_surface, (255, 255, 255, 16), highlight_rect, border_radius=button_radius)
        screen.blit(button_surface, rect.topleft)
        pygame.draw.rect(screen, settings.SHOP_BUTTON_BORDER_COLOR, rect, 2, border_radius=button_radius)

        accent_color = settings.SHOP_ITEM_COLORS.get(item["key"], settings.SHOP_TITLE_COLOR)
        accent_rect = pygame.Rect(rect.x + settings.ui(6), rect.y + settings.ui(6), accent_width, rect.height - settings.ui(12))
        pygame.draw.rect(screen, accent_color, accent_rect, border_radius=accent_width // 2)

        if purchased:
            label_surface = name_font.render(
                i18n.t("shop_owned"), True, settings.SHOP_BUTTON_PURCHASED_TEXT_COLOR
            )
            label_rect = label_surface.get_rect(center=rect.center)
            screen.blit(label_surface, label_rect)
            continue

        text_color = settings.SHOP_BUTTON_TEXT_COLOR if can_afford else settings.SHOP_BUTTON_DISABLED_TEXT_COLOR

        name_surface = name_font.render(i18n.t("shop_" + item["key"]), True, text_color)
        name_pos = (accent_rect.right + settings.ui(12), rect.centery - name_surface.get_height() // 2)
        screen.blit(name_surface, name_pos)

        cost_surface = cost_font.render(str(item["cost"]), True, text_color)
        cost_rect = cost_surface.get_rect()
        cost_rect.midright = (rect.right - padding, rect.centery)
        icon_radius = settings.SHOP_COST_ICON_RADIUS
        icon_center = (cost_rect.left - icon_radius - settings.ui(6), rect.centery)
        _draw_soul_orb(screen, icon_center, icon_radius, glow=False)
        screen.blit(cost_surface, cost_rect)


def draw_game_over(screen):
    """A dark overlay plus centered title/hint text. Fonts are created here
    each call rather than cached -- this screen isn't drawn every frame
    during normal play, only while dead, so it's not worth optimizing."""
    # Sized off the destination surface itself (not the settings screen
    # size) since step 22 draws everything onto a smaller internal
    # surface before it gets scaled up to the real window.
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(settings.GAME_OVER_OVERLAY_ALPHA)
    screen.blit(overlay, (0, 0))

    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2

    title_font = pygame.font.SysFont(None, settings.GAME_OVER_TITLE_FONT_SIZE)
    title_surface = title_font.render(i18n.t("game_over_title"), True, settings.GAME_OVER_TITLE_COLOR)
    title_rect = title_surface.get_rect(center=(center_x, center_y - 20))
    screen.blit(title_surface, title_rect)

    hint_font = pygame.font.SysFont(None, settings.GAME_OVER_HINT_FONT_SIZE)
    hint_surface = hint_font.render(i18n.t("game_over_hint"), True, settings.HUD_TEXT_COLOR)
    hint_rect = hint_surface.get_rect(center=(center_x, center_y + 40))
    screen.blit(hint_surface, hint_rect)


def draw_victory(screen):
    """Step 32: the mirror image of draw_game_over -- same layout (dark
    overlay, centered title, a hint underneath), but green title text and
    different wording, so clearing every base doesn't look like dying."""
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(settings.GAME_OVER_OVERLAY_ALPHA)
    screen.blit(overlay, (0, 0))

    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2

    title_font = pygame.font.SysFont(None, settings.GAME_OVER_TITLE_FONT_SIZE)
    title_surface = title_font.render(i18n.t("victory_title"), True, settings.VICTORY_TITLE_COLOR)
    title_rect = title_surface.get_rect(center=(center_x, center_y - 20))
    screen.blit(title_surface, title_rect)

    hint_font = pygame.font.SysFont(None, settings.GAME_OVER_HINT_FONT_SIZE)
    hint_surface = hint_font.render(i18n.t("victory_hint"), True, settings.HUD_TEXT_COLOR)
    hint_rect = hint_surface.get_rect(center=(center_x, center_y + 40))
    screen.blit(hint_surface, hint_rect)


def get_pause_button_rect(screen):
    """Where the pause button sits, in real window coordinates. A
    separate function (rather than computing this inline in
    draw_pause_button) so main.py can call the exact same math to test
    mouse clicks against it, without waiting for a draw to happen first."""
    size = settings.PAUSE_BUTTON_SIZE
    margin = settings.PAUSE_BUTTON_MARGIN
    x = screen.get_width() - margin - size
    y = margin
    return pygame.Rect(x, y, size, size)


def draw_pause_button(screen):
    """A small square button in the top-right corner, drawn directly on
    the real window -- not on the zoomed internal game surface -- so it
    stays a fixed, crisp size no matter what ZOOM is set to."""
    rect = get_pause_button_rect(screen)
    pygame.draw.rect(screen, settings.PAUSE_BUTTON_COLOR, rect)
    pygame.draw.rect(screen, settings.HEALTH_BAR_BORDER_COLOR, rect, 2)

    # Two vertical bars -- the universal "pause" icon.
    bar_width = max(2, rect.width // 6)
    bar_height = rect.height - 16
    gap = rect.width // 5
    bar_top = rect.top + 8
    left_bar_x = rect.centerx - gap // 2 - bar_width
    right_bar_x = rect.centerx + gap // 2
    pygame.draw.rect(screen, settings.PAUSE_BUTTON_BAR_COLOR, (left_bar_x, bar_top, bar_width, bar_height))
    pygame.draw.rect(screen, settings.PAUSE_BUTTON_BAR_COLOR, (right_bar_x, bar_top, bar_width, bar_height))


def get_stats_button_rect(screen):
    """Step 60: the stats button sits just left of the pause button,
    same size, top-right corner of the real window."""
    pause_rect = get_pause_button_rect(screen)
    size = settings.PAUSE_BUTTON_SIZE
    return pygame.Rect(pause_rect.left - settings.STATS_BUTTON_GAP - size, pause_rect.top, size, size)


def draw_stats_button(screen, active=False):
    """A small square button with a bar-chart icon -- clicking it
    toggles the stats panel (see draw_stats_panel)."""
    rect = get_stats_button_rect(screen)
    color = settings.STATS_BUTTON_ACTIVE_COLOR if active else settings.PAUSE_BUTTON_COLOR
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, settings.HEALTH_BAR_BORDER_COLOR, rect, 2)

    # Three bars of different heights -- a tiny bar chart.
    bar_width = max(3, rect.width // 7)
    gap = max(2, rect.width // 10)
    total_width = bar_width * 3 + gap * 2
    left = rect.centerx - total_width // 2
    base_y = rect.bottom - 10
    for i, bar_height in enumerate((rect.height // 3, rect.height // 2 + 2, rect.height * 2 // 3)):
        pygame.draw.rect(
            screen, settings.PAUSE_BUTTON_BAR_COLOR,
            (left + i * (bar_width + gap), base_y - bar_height, bar_width, bar_height),
        )


def _stat_rows(player):
    """(label, value-string) for every row of the stats panel. Damage /
    attack speed / move speed are the REAL numbers the game uses
    (base * every multiplier from levels and shop buffs), with the total
    bonus over base shown in brackets when there is one."""
    weapon = player.equipped_weapon

    def bonus(multiplier):
        percent = round((multiplier - 1) * 100)
        return f"  (+{percent}%)" if percent > 0 else ""

    damage = weapon.damage * player.damage_multiplier
    shots_per_second = player.attack_speed_multiplier / weapon.fire_interval
    move_speed = settings.PLAYER_SPEED * player.speed_multiplier
    xp_required = player.xp_required_for_next_level()
    if xp_required is None:
        level_text = f"{player.level} ({i18n.t('max')})"
    else:
        level_text = f"{player.level}  ({int(player.xp)}/{xp_required} XP)"

    return [
        (i18n.t("stat_level"), level_text),
        (i18n.t("stat_health"), f"{int(round(player.health))} / {int(round(player.max_health))}"),
        (i18n.t("stat_damage"), f"{damage:.1f}{bonus(player.damage_multiplier)}"),
        (i18n.t("stat_attack_speed"), f"{shots_per_second:.1f}{i18n.t('per_second')}{bonus(player.attack_speed_multiplier)}"),
        (i18n.t("stat_move_speed"), f"{move_speed:.0f}{bonus(player.speed_multiplier)}"),
        (i18n.t("stat_souls"), str(player.souls)),
    ]


def get_stats_panel_rect(screen):
    """Panel hangs just below the stats/pause buttons, right-aligned to
    the pause button's right edge."""
    pause_rect = get_pause_button_rect(screen)
    padding = settings.STATS_PANEL_PADDING
    height = padding * 2 + settings.STATS_PANEL_TITLE_HEIGHT + settings.STATS_PANEL_ROW_COUNT * settings.STATS_PANEL_ROW_HEIGHT
    width = settings.STATS_PANEL_WIDTH
    return pygame.Rect(pause_rect.right - width, pause_rect.bottom + settings.ui(10), width, height)


def draw_stats_panel(screen, player):
    """Step 60: every player stat in one place -- level/xp, health,
    damage, attack speed, move speed, equipped weapon, souls. Shown
    while the stats button is toggled on; drawn on the real screen."""
    rect = get_stats_panel_rect(screen)
    radius = settings.STATS_PANEL_BORDER_RADIUS
    padding = settings.STATS_PANEL_PADDING

    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, settings.STATS_PANEL_BG_COLOR, panel.get_rect(), border_radius=radius)
    screen.blit(panel, rect.topleft)
    pygame.draw.rect(screen, settings.STATS_PANEL_BORDER_COLOR, rect, 2, border_radius=radius)

    title_font = pygame.font.SysFont(None, settings.STATS_PANEL_TITLE_FONT_SIZE, bold=True)
    title = title_font.render(i18n.t("stats_title"), True, settings.STATS_PANEL_TITLE_COLOR)
    screen.blit(title, (rect.x + padding, rect.y + padding))
    divider_y = rect.y + padding + settings.STATS_PANEL_TITLE_HEIGHT - 6
    pygame.draw.line(
        screen, settings.STATS_PANEL_DIVIDER_COLOR,
        (rect.x + padding, divider_y), (rect.right - padding, divider_y), 2,
    )

    label_font = pygame.font.SysFont(None, settings.STATS_PANEL_FONT_SIZE)
    value_font = pygame.font.SysFont(None, settings.STATS_PANEL_FONT_SIZE, bold=True)
    y = rect.y + padding + settings.STATS_PANEL_TITLE_HEIGHT
    for label, value in _stat_rows(player):
        label_surface = label_font.render(label, True, settings.STATS_PANEL_LABEL_COLOR)
        value_surface = value_font.render(value, True, settings.STATS_PANEL_VALUE_COLOR)
        row_mid = y + settings.STATS_PANEL_ROW_HEIGHT // 2
        screen.blit(label_surface, label_surface.get_rect(midleft=(rect.x + padding, row_mid)))
        screen.blit(value_surface, value_surface.get_rect(midright=(rect.right - padding, row_mid)))
        y += settings.STATS_PANEL_ROW_HEIGHT


def get_continue_button_rect(screen):
    """The pause overlay's Continue button -- top of the stack."""
    rect = pygame.Rect(0, 0, settings.PAUSE_LEAVE_BUTTON_WIDTH, settings.PAUSE_LEAVE_BUTTON_HEIGHT)
    rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 30)
    return rect


def get_settings_button_rect(screen):
    """Sits just below Continue."""
    rect = get_continue_button_rect(screen)
    rect.y += settings.PAUSE_LEAVE_BUTTON_HEIGHT + settings.ui(18)
    return rect


def get_leave_button_rect(screen):
    """Same idea as get_pause_button_rect: main.py needs this exact rect
    to test clicks, so it lives in its own function rather than only
    inside draw_pause_overlay. Bottom of the stack (Continue, Settings, Leave)."""
    rect = get_settings_button_rect(screen)
    rect.y += settings.PAUSE_LEAVE_BUTTON_HEIGHT + settings.ui(18)
    return rect


def draw_pause_overlay(screen):
    """Dark overlay, a "PAUSED" title, and a single Leave button. Drawn
    directly on the real window, same reasoning as the pause button."""
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(settings.PAUSE_OVERLAY_ALPHA)
    screen.blit(overlay, (0, 0))

    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2

    title_font = pygame.font.SysFont(None, settings.PAUSE_TITLE_FONT_SIZE)
    title_surface = title_font.render(i18n.t("paused"), True, settings.HUD_TEXT_COLOR)
    title_rect = title_surface.get_rect(center=(center_x, center_y - 60))
    screen.blit(title_surface, title_rect)

    button_font = pygame.font.SysFont(None, settings.PAUSE_LEAVE_BUTTON_FONT_SIZE)
    for button_rect, label in (
        (get_continue_button_rect(screen), i18n.t("continue")),
        (get_settings_button_rect(screen), i18n.t("settings")),
        (get_leave_button_rect(screen), i18n.t("leave")),
    ):
        pygame.draw.rect(screen, settings.PAUSE_LEAVE_BUTTON_COLOR, button_rect)
        pygame.draw.rect(screen, settings.HEALTH_BAR_BORDER_COLOR, button_rect, 2)
        button_text = button_font.render(label, True, settings.PAUSE_LEAVE_BUTTON_TEXT_COLOR)
        screen.blit(button_text, button_text.get_rect(center=button_rect.center))