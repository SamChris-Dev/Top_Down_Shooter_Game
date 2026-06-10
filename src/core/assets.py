import os
import pygame
import xml.etree.ElementTree as ET

class AssetManager:
    """Centralized asset manager for caching images, sounds, and fonts."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.spritesheets = {}
        
        import sys
        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.assets_dir = os.path.join(self.base_dir, 'assets')

    def load_image(self, path, key=None, colorkey=None, alpha=True):
        if key is None:
            key = path
        if key in self.images:
            return self.images[key]
            
        full_path = os.path.join(self.assets_dir, path)
        try:
            image = pygame.image.load(full_path)
            if alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
                if colorkey is not None:
                    image.set_colorkey(colorkey)
            self.images[key] = image
            return image
        except pygame.error as e:
            print(f"Cannot load image: {path} - {e}")
            # Fallback surface
            surface = pygame.Surface((64, 64))
            surface.fill((255, 0, 255))
            self.images[key] = surface
            return surface

    def load_sound(self, path, key=None):
        if key is None:
            key = path
        if key in self.sounds:
            return self.sounds[key]
            
        full_path = os.path.join(self.assets_dir, path)
        try:
            sound = pygame.mixer.Sound(full_path)
            self.sounds[key] = sound
            return sound
        except (pygame.error, FileNotFoundError) as e:
            print(f"Cannot load sound: {path} - {e}")
            self.sounds[key] = None
            return None

    def get_font(self, name, size):
        key = f"{name}_{size}"
        if key in self.fonts:
            return self.fonts[key]
            
        try:
            font = pygame.font.match_font(name)
            font_obj = pygame.font.Font(font, size)
            self.fonts[key] = font_obj
            return font_obj
        except Exception as e:
            print(f"Cannot load font: {name} - {e}")
            font_obj = pygame.font.Font(None, size) # Fallback to default
            self.fonts[key] = font_obj
            return font_obj

    def load_spritesheet(self, img_path, xml_path, key):
        if key in self.spritesheets:
            return self.spritesheets[key]
            
        full_img = os.path.join(self.assets_dir, img_path)
        full_xml = os.path.join(self.assets_dir, xml_path)
        
        try:
            spritesheet = pygame.image.load(full_img).convert_alpha()
            frames = {}
            tree = ET.parse(full_xml)
            root = tree.getroot()
            for subtexture in root.findall('SubTexture'):
                name = subtexture.get('name')
                x = int(subtexture.get('x'))
                y = int(subtexture.get('y'))
                width = int(subtexture.get('width'))
                height = int(subtexture.get('height'))
                
                image = pygame.Surface((width, height), pygame.SRCALPHA)
                image.blit(spritesheet, (0, 0), (x, y, width, height))
                frames[name] = image
                
            self.spritesheets[key] = frames
            return frames
        except Exception as e:
            print(f"Cannot load spritesheet {key}: {e}")
            self.spritesheets[key] = {}
            return {}
            
    def get_sprite(self, sheet_key, sprite_name, fallback_size=(64, 64), fallback_color=(0, 255, 0)):
        if sheet_key in self.spritesheets and sprite_name in self.spritesheets[sheet_key]:
            return self.spritesheets[sheet_key][sprite_name]
            
        # Create a fallback surface
        fallback = pygame.Surface(fallback_size, pygame.SRCALPHA)
        fallback.fill(fallback_color)
        return fallback

asset_manager = AssetManager()
