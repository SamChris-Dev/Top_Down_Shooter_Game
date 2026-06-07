import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_width, screen_height):
        super().__init__() # Initialize the parent Sprite class
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 5
        
        # Load and scale the player image
        try:
            # .convert_alpha() optimizes the image format for faster rendering and handles transparency
            self.image = pygame.image.load("assets/aim.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
        except pygame.error as e:
            print(f"Could not load image: {e}")
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 255, 255))
            
        # The 'rect' controls the position and collision boundaries of the sprite
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    # Renaming handle_keys to 'update' integrates it with Pygame's Sprite Groups
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Movement logic updating the rect's position directly
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.rect.left > 0:
            self.rect.x -= self.speed
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.rect.right < self.screen_width:
            self.rect.x += self.speed
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.rect.top > 0:
            self.rect.y -= self.speed
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.rect.bottom < self.screen_height:
            self.rect.y += self.speed