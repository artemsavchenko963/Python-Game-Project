"""
Step 2: draw a stationary colored square (our future player) in the middle
of the window. Still no movement -- just getting something on screen.
"""

import pygame

import settings


def main():
    pygame.init()
    pygame.display.set_caption("Dark Rooms")
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # A pygame.Rect describing where the player square is: x, y, width, height.
    # We start it centered on the screen.
    player_rect = pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE)
    player_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)

    running = True
    while running:
        # 1. Handle input/events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Update game state (nothing moves yet)

        # 3. Draw everything
        screen.fill(settings.BG_COLOR)
        pygame.draw.rect(screen, settings.PLAYER_COLOR, player_rect)
        pygame.display.flip()

        # 4. Wait so we run at a steady FPS instead of maxing out the CPU
        clock.tick(settings.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()