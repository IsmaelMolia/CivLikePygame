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
        self.custom_cursor(CURSORS_FILEPATHS["default"])

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

    def check_events(self):
        for event in pygame.event.get():
            if self.ui.button_handler.current_input_mode == True:
                self.ui.button_handler.event_input(event)
            if event.type == pygame.QUIT:
                self.playing = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.ui.button_handler.not_input_mode()
                self.ui.button_handler.check_buttons()
            elif event.type == pygame.MOUSEWHEEL:
                self.map.zoom_camera(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.ui.button_handler.toggle_side_page("PAUSE", not self.ui.page_handler.pause)
                    self.map.reset_camera() # temporaire, car bugs :/
                elif event.key == pygame.K_TAB:
                    self.map.fog_of_war = not self.map.fog_of_war
                elif event.key == pygame.K_a:
                    self.map.make_city()
                elif event.key == pygame.K_SPACE:
                    self.map.player_handler.next_turn()
                elif event.key == pygame.K_e:
                    self.map.change_vision_mode(["empire"], [not self.map.vision_modes["empire"]])
                elif event.key == pygame.K_r:
                    self.map.change_vision_mode(["ressources"], [not self.map.vision_modes["ressources"]])
                elif event.key == pygame.K_b:
                    self.ui.button_handler.toggle_side_page("BUILD", not self.ui.page_handler.state_side_pages["BUILD"])
                elif event.key == pygame.K_1:
                    self.ui.button_handler.select_current_unit()
                elif event.key == pygame.K_2:
                    self.ui.button_handler.select_current_building()
        
        if self.ui.page_handler.page == 5:
            keys = pygame.key.get_pressed() # pour les touches sur lesquelles on peut rester appuyé (ex : pas besoin de mitrailler Z pour bouger la camera vers le haut)
            if keys[pygame.K_d] or keys[pygame.K_q] or keys[pygame.K_s] or keys[pygame.K_z]:
                self.map.move_camera(keys)
            elif keys[pygame.K_c]:
                self.map.reset_camera()

    def game_loop(self):
        self.ui.page_handler.full_reload()

        while self.playing:
            self.delta = self.clock.tick(60)
            self.check_events()
            self.ui.show()
            pygame.display.update()
        
        self.saves_handler.make_data()
        self.saves_handler.save_settings()
        self.saves_handler.write_save()

# à faire / savoir :
# - detecter autrement comment souris est sur tile (convertir coordonnes souris, ne pas verifier distance avec chaque tile)
# - ajouter plusieurs visions de maps (ressources, empires, unités...)
# - creer debut jeu (pouvoir creer ville, s expandre, construir, faire unités...)
# - ajouter mini map (au final non, et si oui pas une priorité)
# - changer animated_sea() et remplacer par des vagues seulement sur les bords des tiles qui touchent mer ?
# - ajouter pathfinding (avec mouvement par unité + cout par type de tile)
# - essayer de reduire taille des saves ?
# - dans get_inputs() de ButtonHanlder, certains boutons très répétitifs mais flemme d optimiser
# - ameliorer generation ? :
#       - ordre d expansion (par exemple mountains en premier et forest en dernier ?)
#       - priorité d expansion (juste expandre biomes dans empty_tiles, ou sinon proba de voler une tile a un autre biome ? et si oui besoin de priorité ? (ex : forest > plain))
#       - probabilite d expansion garantie si taille biome inferieure a taille minimale, sinon pourcentage proportionnel a taille actuelle vs taille max (de 100% a 0% plus la taille se rapproche de taille max)
#       - expand les seeds chacune leur tour ? (for seed in seeds: tile +1, jusqu'a ce que len(empty_tiles) == 0)
#       - expandre de force biomes plus petits que taille minimum ?
#       - expansion differente pour chaque biome ? (ex : faire une chaine de montagne, faire une riviere/un lac, faire collines aux alentours de montagnes, faire forets au centre de plaines...) (pour rendre + realiste)
#       - ajouter accès à l océan + faire plusieurs iles ?
# - ajouter production (prod par ressource : 1/food, 2/wood, 3/rock, strategic_ressources...) ?
#   -> donc cout unités et batiments en ressources et vitesse production depend de prod ? (unites et buildings basiques coutent food, puis autre ressources pour tiers plus élevés)
#   -> prod liée à une ville et non pas à tout l empire ?
# - mieux optimiser tile.draw_background() (on pourrait juste remettre toutes les tiles à la normale quand on active pause, pas besoin de self.update() à chaque frame, seulemnt si pause == False)
# - essayer d optimiser check_side_pages() ?
# - quand on construit un building, mettre en vert les tiles sur lesquelles on peut le construire (bon terrain, bon owner, cité locale, pas de building, etc...) et en rouge les autres
# - essayer d empecher les players de spawn trop à proximité les uns des autres ?
# - optimiser update_tile_size() ? (car a chaque mouvement de camera toutes les tiles sont recalculées)
# - dans move_camera(), j espere qu utiliser des float pour la camera ne vas pas tout casser :)
# - ajouter strategic ressources (et si possible essayer de bien répartir leur spawn equitablement)
# - est-ce un probleme de faire "from units import *" dans map.py et dans players.py ? faut-il le faire seulement dans 1 seule file ?
# - que faire si get_settler_possibilities() ne renvoie aucune possibibilité (très improbable, mais peut etre possible ?) ou si la taille de la map est trop petite ?
# - ajouter vision production ? ou mettre dans vision ressources ?
# - mode inspect unit / building (un seul peut etre activé a la fois, a mettre entre UNIT/BUILDING et TILE, ne pas oublier de desactiver quand TILE et donc UNIT/BUILDING est désactivé)
#   -> montrera stats units, petit texte de description, image agrandie de l unit/building, etc...
# - optimiser generation map pour pouvoir generer maps tres, tres grandes (et donc optimiser seed_generation_v3(), car le lag vient de la)
# - mettre rappel au premier tour de jeu d'appuyer sur ESC puis HELP ?
# - changer curseur CURRENT_UNIT en fonction de ce que la souris est en train de hover (ex : mettre une épée si souris au dessus d un ennemi) ?
# - remplacer "pause" par "state_side_pages["PAUSE"]" ?
# - probleme actuel de tiles_seen : copie les tiles et pas juste les coo ? à changer pour la sauvegarde
# - optimiser draw_highlighted_unit() ?
# - mieux optimiser ui_icons() ?
# - comment faire si trop de ressources ? comment faire pour que texte du bouton ne deborde pas ? rendre taille des boutons types ressources/income de ressources proportionnelle à taille texte avec une fonction ?
# - peut etre que si une ressource importante dans le negatif (genre nourriture) retirer 10% de la vie de toutes les units par tour ? 
# - faire un game over ?
# - optimiser map.draw_tiles() ? -> vraiment pas optimisé mais flemme :)
# - comment faire si frontieres entre 2 joueurs ? comment savoir quel background dessiner en priorité ?
# - optimiser tile.draw_ressources() ? (car vraiment pas optimisé :/ 
# - ajouter affichage prod (prod tile = ressources + building ?)
# - pouvoir calculer les ressources d une ville en particulier (et non pas de tout l empire) (notamment pour calculer prod pour construction et food pour expansion)
# - ajouter expansion automatique ville (qui dépend de l'income en food de la ville : par exemple 10 de food pour la premiere tile, puis +2 par nouvelle tile) (nouvele tile = tile aleatoire voisine de la ville et sans owner)
# - faire une side_page building_action (pour city, on peut creer quartiers et units, pour autres batiments prod d unités, etc...)
# - faire plusieurs niveaux de buildings avec une nouvelle classe par niveau ? (ex : City_lvl_2)
# - trouver un raccourci pour side_page CURRENT_BUILDING -> peut etre 1 pour switcher vers CURRENT_UNIT et 2 pour switcher vers CURRENT_BUILDING
# - essayer d optimiser update_tile_size() car sur map trop grande beaucoup trop de lag -> peut etre update et afficher seulement les tiles vsisibles (celles dans le champ de la camera)
# - les liens entre tiles et units vont dans les 2 sens (ex : tile.unit = unit et unit.tile_linked = tile), est ce que c est un probleme ?
# - peut etre que maintenant qu on peut activer current_unit avec 1 enlever RMB

# AVANT D ESSAYER DE RENDRE LE JEU PLUS BEAU ET D OPTIMISER, RENDRE LE JEU JOUABLE !!!!!!!
