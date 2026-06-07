import pygame

class Player:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = 50
        self.height = 50
        self.color = (255, 255, 255)  # White
        self.speed = 5

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        
        # Movement logic with boundary checks
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.x > 0:
            self.x -= self.speed
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.x < self.screen_width - self.width:
            self.x += self.speed
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.y > 0:
            self.y -= self.speed
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.y < self.screen_height - self.height:
            self.y += self.speed

    def draw(self, surface):
        # Draw the player as a simple rectangle
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
