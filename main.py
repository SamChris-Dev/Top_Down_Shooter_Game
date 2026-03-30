import pygame
import sys

# 1. Initialize Pygame
pygame.init()

# 2. Set up the display (Width, Height)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Top-Down-Shooter!")

# 3. Colors (RGB)
BLUE = (30, 144, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 4. The Game Loop
running = True
while running:
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with color
    screen.fill(BLUE)

    # Draw a simple shape (Surface, Color, [x, y, width, height])
    pygame.draw.rect(screen, WHITE, [350, 250, 100, 100])

    # Update the display
    pygame.display.flip()

# 5. Clean up
pygame.quit()
sys.exit()