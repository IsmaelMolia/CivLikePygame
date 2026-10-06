import pygame
from game import Game

def main():
    pygame.init()
    
    game = Game()
    game.game_loop()

    pygame.quit()

main()
