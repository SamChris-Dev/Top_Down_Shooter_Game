import sys
import os

# Add src folder to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine import Game

if __name__ == "__main__":
    g = Game()
    g.menu.show_start_screen()
    
    while g.running:
        g.new()
        g.menu.show_go_screen()
