import pygame
import sys
from player_movement import Player

# 1. Initialize Pygame
pygame.init()

# 2. Set up the display (Width, Height)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down-Shooter!")

# 3. Colors (RGB)
BLUE = (30, 144, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 4. Initialize Player
player = Player(WIDTH // 2, HEIGHT // 2, WIDTH, HEIGHT)

# 5. Clock to control frame rate
clock = pygame.time.Clock()

# 6. The Game Loop
running = True
while running:
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle Player Movement
    player.handle_keys()

    # Fill the screen with color
    screen.fill(BLUE)

    # Draw Player
    player.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 60 FPS
    clock.tick(60)

# 7. Clean up
pygame.quit()
sys.exit()