import pygame

class Player:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = 50
        self.height = 50
        self.speed = 5
        
        # Load and scale the player image
        try:
            self.image = pygame.image.load("assets/aim.png")
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except pygame.error as e:
            print(f"Could not load image: {e}")
            # Fallback to a surface if image fails to load
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((255, 255, 255))

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
        # Draw the player image
        surface.blit(self.image, (self.x, self.y))

