"""
Step 3: move the square with WASD. Movement speed is in pixels-per-second
and multiplied by dt (time since last frame), so it moves at the same real
-world speed no matter how fast or slow the computer renders frames.

No walls yet -- you can walk off the edge of the screen. That's step 4.
"""

import pygame

import settings


def main():
    pygame.init()
    pygame.display.set_caption("Dark Rooms")
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

     # the player isn't allowed to leave.
    bounds_rect = screen.get_rect()
    # A pygame.Rect describing where the player square is: x, y, width, height.
    # We start it centered on the screen.
    player_rect = pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE)
    player_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)

    dt = 0  # time (seconds) since the last frame; updated at the end of each loop
    running = True
    while running:
        # 1. Handle input/events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Update game state
        # pygame.key.get_pressed() returns the CURRENT state of every key,
        # so movement keeps happening for as long as a key is held down
        # (unlike pygame.KEYDOWN events, which only fire once per press).
        keys = pygame.key.get_pressed()
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

        player_rect.x += dx * settings.PLAYER_SPEED * dt
        player_rect.y += dy * settings.PLAYER_SPEED * dt

        # poking out on any side -- this is what stops the player at the edges.
        player_rect.clamp_ip(bounds_rect)

        # 3. Draw everything
        screen.fill(settings.BG_COLOR)
        pygame.draw.rect(screen, settings.PLAYER_COLOR, player_rect)
        pygame.display.flip()

        # 4. Wait so we run at a steady FPS, and remember how long that frame
        #    actually took (dt = "delta time", in seconds) for next frame's movement math.
        dt = clock.tick(settings.FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()