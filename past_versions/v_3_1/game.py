import pygame
from constants import *
from ui import *
from map import *
from saves_handler import *

class Game:
    def __init__(self):
        self.playing = True

        self.w, self.h = W, H
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("GAME") # temporaire ?
        self.custom_cursor(CURSOR_FILEPATH)

        self.clock = pygame.time.Clock()
        self.delta = 0 # pour l instant inutile

        self.ui = UI(self)
        self.map = Map(self)
        self.saves_handler = Saves_Handler(self)

    def custom_cursor(self, filepath):
        #pygame.mouse.set_cursor(pygame.mouse.get_pos(), pygame.image.load(filepath))
        try:
            pygame.mouse.set_cursor((0, 0), pygame.image.load(filepath))
        except Exception:
            pass

    def event_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.ui.button_handler.current_input = self.ui.button_handler.current_input[:-1]
            elif event.key == pygame.K_RETURN:
                self.ui.button_handler.return_input()
            else:
                self.ui.button_handler.current_input += event.unicode

    def check_events(self):
        for event in pygame.event.get():
            if self.ui.button_handler.current_input_mode == True:
                self.event_input(event)
            if event.type == pygame.QUIT:
                self.playing = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.ui.deactivate_input_mode()
                self.ui.check_buttons()
            elif event.type == pygame.MOUSEWHEEL:
                self.map.zoom_camera(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.ui.button_handler.pause_menu()
        keys = pygame.key.get_pressed()
        if self.ui.page == 5:
            if keys[pygame.K_d] or keys[pygame.K_q] or keys[pygame.K_s] or keys[pygame.K_z]:
                    self.map.move_camera(keys)

    def game_loop(self):
        self.ui.full_reload()

        while self.playing:
            self.delta = self.clock.tick(60)
            self.check_events()
            self.ui.load_background()
            self.map.update_camera()
            self.map.draw_tiles()
            self.ui.show_buttons()
            pygame.display.update()
        
        self.saves_handler.make_data()
        self.saves_handler.save_settings()
        self.saves_handler.write_save()

# à faire :
# - probleme actuel : je dois faire beaucoup trop de choses manuellement (exemple : quand je rajoute un bouton, je dois penser à faire beaucoup d'autres modifications)
#                     et je dois donc me rappeler de tout (et je peux facilement oublier), il faudrait donc essayer de rendre beaucoup de choses automatiques
# - pouvoir supprimer 1 seule sauvegarde
# - detecter autrement comment souris est sur tile (convertir coordonnes souris, ne pas verifier distance avec chaque tile)
# - afficher donnees tile quand souris passe dessus
# - ajouter side_buttons
# - ajouter infos supplementaires tiles quand cliquées
# - different types tiles
# - differentes ressources tiles
# - generation map
# - ajouter plusieurs visions de maps (ressources, empires, unités...)
# - creer debut jeu (pouvoir creer ville, s expandre, construir, faire unités...)
# - ajouter mini map
# - ajouter fog of war
# - changer animated_sea() et remplacer par des vagues seulement sur les bords des tiles qui touchent mer ?
# - ameliorer limite deplacement camera
# - ameliorer menu pause (pourquoi tile_number_factor revient a sa taille initiale...?) (et en plus les tiles ne s updatent pas quand tile_number_factor reset)
# - ajouter unités
# - ajouter pathfinding (avec mouvement par unité + cout par type de tile)
