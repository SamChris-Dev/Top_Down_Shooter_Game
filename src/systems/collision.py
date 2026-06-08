import pygame

def collide_hit_rect(one, two):
    """Callback for sprite collisions using hit_rect instead of rect."""
    return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
    """Generic wall collision function for entities with a hit_rect and vel."""
    if dir == 'x':
        hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if getattr(sprite, 'vx', 0) > 0 or getattr(sprite, 'vel', pygame.math.Vector2()).x > 0:
                sprite.hit_rect.right = hits[0].rect.left
            if getattr(sprite, 'vx', 0) < 0 or getattr(sprite, 'vel', pygame.math.Vector2()).x < 0:
                sprite.hit_rect.left = hits[0].rect.right
            
            if hasattr(sprite, 'vx'):
                sprite.vx = 0
            if hasattr(sprite, 'vel'):
                sprite.vel.x = 0
            sprite.pos.x = sprite.hit_rect.centerx
            
    if dir == 'y':
        hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if getattr(sprite, 'vy', 0) > 0 or getattr(sprite, 'vel', pygame.math.Vector2()).y > 0:
                sprite.hit_rect.bottom = hits[0].rect.top
            if getattr(sprite, 'vy', 0) < 0 or getattr(sprite, 'vel', pygame.math.Vector2()).y < 0:
                sprite.hit_rect.top = hits[0].rect.bottom
            
            if hasattr(sprite, 'vy'):
                sprite.vy = 0
            if hasattr(sprite, 'vel'):
                sprite.vel.y = 0
            sprite.pos.y = sprite.hit_rect.centery
