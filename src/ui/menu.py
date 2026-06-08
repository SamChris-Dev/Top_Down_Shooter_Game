import pygame
import sys
from core.settings import *

class Menu:
    def __init__(self, game):
        self.game = game

    def draw_text(self, text, size, color, x, y, align="nw"):
        font = self.game.asset_manager.get_font('arial', size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "center":
            text_rect.center = (x, y)
        self.game.screen.blit(text_surface, text_rect)

    def show_start_screen(self):
        self.game.screen.fill(BLACK)
        self.draw_text(TITLE, 64, WHITE, WIDTH / 2, HEIGHT / 4, align="center")
        self.draw_text("WASD to move, Mouse to aim/shoot, LSHIFT to sprint", 22, WHITE, WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press 'E' to switch weapons", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40, align="center")
        self.draw_text("Press any key to play", 36, YELLOW, WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pygame.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        if not self.game.running:
            return

        self.game.screen.fill(BLACK)
        self.draw_text("GAME OVER", 64, RED, WIDTH / 2, HEIGHT / 4, align="center")
        
        from systems.save_manager import save_manager
        wave = self.game.wave_manager.current_wave if hasattr(self.game, 'wave_manager') else 1
        best = save_manager.get("best_wave", 1)
        
        self.draw_text(f"You reached Wave {wave}", 30, WHITE, WIDTH / 2, HEIGHT / 2, align="center")
        if wave >= best:
            self.draw_text("NEW BEST!", 30, YELLOW, WIDTH / 2, HEIGHT / 2 + 40, align="center")
            
        self.draw_text("Press any key to restart", 36, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pygame.display.flip()
        self.wait_for_key()

    def show_pause_screen(self):
        dim_screen = pygame.Surface(self.game.screen.get_size()).convert_alpha()
        dim_screen.fill((0, 0, 0, 180))
        self.game.screen.blit(dim_screen, (0, 0))
        self.draw_text("PAUSED", 64, RED, WIDTH / 2, HEIGHT / 2 - 50, align="center")
        self.draw_text("Press ESC to resume", 24, WHITE, WIDTH / 2, HEIGHT / 2 + 50, align="center")
        pygame.display.flip()

    def wait_for_key(self):
        pygame.event.clear()
        waiting = True
        while waiting:
            self.game.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.game.running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    waiting = False
