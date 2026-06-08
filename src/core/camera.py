import pygame
from core.settings import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        target_x = -target.rect.centerx + int(WIDTH / 2)
        target_y = -target.rect.centery + int(HEIGHT / 2)

        current_x = self.camera.x
        current_y = self.camera.y

        # Interpolate
        new_x = current_x + (target_x - current_x) * CAMERA_LERP_SPEED
        new_y = current_y + (target_y - current_y) * CAMERA_LERP_SPEED

        self.camera = pygame.Rect(int(new_x), int(new_y), self.width, self.height)
