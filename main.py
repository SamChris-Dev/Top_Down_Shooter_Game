import pygame
import sys
from player_movement import Player

# 1. Initialize Pygame
pygame.init()

# 2. Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down-Shooter!")

# 3. Colors
BLUE = (30, 144, 255)

# 4. Initialize Player and Sprite Group
player = Player(WIDTH // 2, HEIGHT // 2, WIDTH, HEIGHT)

# Create a group and add the player to it
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# 5. Clock to control frame rate
clock = pygame.time.Clock()

# 6. The Game Loop
running = True
while running:
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update all sprites in the group simultaneously
    # This automatically calls the update() method we defined in the Player class
    all_sprites.update()

    # Fill the screen with color
    screen.fill(BLUE)

    # Draw all sprites in the group to the screen automatically
    all_sprites.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate to 60 FPS
    clock.tick(60)

# 7. Clean up
pygame.quit()
sys.exit()