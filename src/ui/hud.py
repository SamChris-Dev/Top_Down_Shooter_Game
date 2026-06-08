import pygame
from core.settings import *

class HUD:
    def __init__(self, game):
        self.game = game
        self.font = game.asset_manager.get_font('arial', 24)

    def draw_text(self, text, size, color, x, y, align="nw"):
        font = self.game.asset_manager.get_font('arial', size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        elif align == "ne":
            text_rect.topright = (x, y)
        elif align == "sw":
            text_rect.bottomleft = (x, y)
        elif align == "se":
            text_rect.bottomright = (x, y)
        elif align == "center":
            text_rect.center = (x, y)
        self.game.screen.blit(text_surface, text_rect)

    def draw(self):
        if not hasattr(self.game, 'player') or not self.game.player.alive():
            return
            
        player = self.game.player
        
        # Health Bar
        bar_width = 200
        bar_height = 20
        health_ratio = max(0, player.health / PLAYER_HEALTH)
        fill_width = int(bar_width * health_ratio)
        
        outline_rect = pygame.Rect(20, 20, bar_width, bar_height)
        fill_rect = pygame.Rect(20, 20, fill_width, bar_height)
        
        pygame.draw.rect(self.game.screen, RED, fill_rect)
        pygame.draw.rect(self.game.screen, WHITE, outline_rect, 2)
        
        self.draw_text(f"HP: {int(player.health)}", 20, WHITE, 25, 20, align="nw")
        
        # Weapon Info
        weapon = player.current_weapon
        ammo_text = "Reloading..." if weapon.is_reloading else f"{weapon.current_ammo} / {weapon.reserve_ammo}"
        if weapon.name == "Pistol" and not weapon.is_reloading:
             ammo_text = f"{weapon.current_ammo} / \u221E" # Infinity symbol
        self.draw_text(f"Weapon: {weapon.name}  |  Ammo: {ammo_text}", 24, WHITE, 20, 50, align="nw")
        
        # Dash Cooldown Indicator
        now = pygame.time.get_ticks()
        dash_ready = now - player.last_dash_time > player.dash_cooldown
        dash_color = GREEN if dash_ready else RED
        dash_text = "Dash Ready" if dash_ready else "Dash Cooldown"
        self.draw_text(f"[{dash_text}]", 20, dash_color, 20, 80, align="nw")
        
        # Score
        self.draw_text(f"Score: {player.score}", 30, YELLOW, WIDTH - 20, 20, align="ne")
        
        # Wave Info
        if hasattr(self.game, 'wave_manager'):
            wave = self.game.wave_manager.current_wave
            alive = self.game.wave_manager.zombies_alive
            to_spawn = self.game.wave_manager.zombies_to_spawn
            self.draw_text(f"Wave: {wave}", 30, YELLOW, WIDTH / 2, 20, align="center")
            self.draw_text(f"Enemies: {alive + to_spawn}", 24, WHITE, WIDTH / 2, 50, align="center")
            
        # Score/Kills (if implemented)
        from systems.save_manager import save_manager
        best_wave = save_manager.get("best_wave", 1)
        self.draw_text(f"Best Wave: {best_wave}", 24, LIGHT_GRAY, WIDTH - 20, 20, align="ne")
