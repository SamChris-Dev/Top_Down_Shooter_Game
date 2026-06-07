import sys
import os

# This forces Python to recognize the 'src' folder as the working directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine import Game

if __name__ == "__main__":
    # Instantiate the engine
    g = Game()
    g.show_start_screen()
    
    # Run the main menu or game loop
    while g.running:
        g.new()
        g.show_go_screen()
