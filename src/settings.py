# src/settings.py
import pygame

# Screen settings
WIDTH, HEIGHT = 1024, 768
FPS = 60
TITLE = "Top Down Villa Defense"

# Colors
BG_COLOR = (40, 40, 40)

# Grid Settings (Kenney tiles are usually 64x64 or 128x128)
TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Player Settings
PLAYER_SPEED = 300 # Pixels per second (because we will use Delta Time)

# Bullet Settings
BULLET_SPEED = 500
BULLET_LIFETIME = 1000
BULLET_RATE = 150
BULLET_DAMAGE = 25

# Zombie Settings
ZOMBIE_SPEED = 75
ZOMBIE_HEALTH = 100