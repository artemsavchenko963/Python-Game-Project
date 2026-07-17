"""
Step 1: open a window, fill it with a dark background, close cleanly on the X button.
No player, no movement yet -- just proving the window + game loop works.
"""

import pygame

import settings


def main():
    pygame.init()
    pygame.display.set_caption("Dark Rooms")
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    running = True
    while running:
        # 1. Handle input/events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Update game state (nothing to update yet)

        # 3. Draw everything
        screen.fill(settings.BG_COLOR)
        pygame.display.flip()

        # 4. Wait so we run at a steady FPS instead of maxing out the CPU
        clock.tick(settings.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
