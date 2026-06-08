# src/camera.py
import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        # The camera is just a rectangle that represents our viewport
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Shifts the entity's rectangle by the camera's offset
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
       # Target coordinates where we WANT the camera to be
        target_x = -target.rect.centerx + int(WIDTH / 2)
        target_y = -target.rect.centery + int(HEIGHT / 2)

        # Lerp factor (lower = smoother/slower, 1.0 = instant snap)
        # Multiply by delta time in engine for frame-independent lerping, 
        # but a fixed small constant works well for Pygame
        lerp_speed = 0.1 

        # Current camera coordinates
        current_x = self.camera.x
        current_y = self.camera.y

        # Interpolate
        new_x = current_x + (target_x - current_x) * lerp_speed
        new_y = current_y + (target_y - current_y) * lerp_speed

        self.camera = pygame.Rect(int(new_x), int(new_y), self.width, self.height)