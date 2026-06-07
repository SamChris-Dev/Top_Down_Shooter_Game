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
        # Center the camera on the target (usually the player)
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # Update the camera's offset rectangle
        self.camera = pygame.Rect(x, y, self.width, self.height)