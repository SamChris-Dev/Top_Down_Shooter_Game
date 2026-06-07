import pygame
import xml.etree.ElementTree as ET

class Spritesheet:
    def __init__(self, img_path, xml_path):
        self.spritesheet = pygame.image.load(img_path).convert_alpha()
        self.frames = {}
        self.parse_xml(xml_path)

    def parse_xml(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for subtexture in root.findall('SubTexture'):
            name = subtexture.get('name')
            x = int(subtexture.get('x'))
            y = int(subtexture.get('y'))
            width = int(subtexture.get('width'))
            height = int(subtexture.get('height'))
            
            # Extract the specific frame from the spritesheet
            image = pygame.Surface((width, height), pygame.SRCALPHA)
            image.blit(self.spritesheet, (0, 0), (x, y, width, height))
            
            # Save it to our dictionary
            self.frames[name] = image

    def get_image(self, name):
        return self.frames.get(name)
