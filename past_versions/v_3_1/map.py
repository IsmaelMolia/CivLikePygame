import pygame
import math
from random import randint
from constants import *

class Tile:
    def __init__(self, game, coo, center, inner_radius, outer_radius, color=(0, 225, 0), background_color=(180, 125, 0)):
        self.game = game
        self.map = self.game.map

        self.coo = coo
        self.center = center
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        
        self.color = color
        self.initial_color = color
        self.background_color = background_color
        
        self.points = self.get_points()
        self.background_points = self.get_background_points()
        self.position = pygame.Vector2(self.center[0], self.center[1])

    def get_points(self):
        points = []
        for i in range(6):
            angle = math.pi / 180 * ((60 * i - 30) % 360)
            point = round(self.center[0] + self.outer_radius * math.cos(angle)), round(self.center[1] + self.outer_radius * math.sin(angle))
            points.append(point)
        return points
    
    def get_background_points(self):
        points = []
        factor = 1.3
        for i in range(6):
            angle = math.pi / 180 * ((60 * i - 30) % 360)
            point = round(self.center[0] + self.outer_radius * math.cos(angle) * factor), round(self.center[1] + self.outer_radius * math.sin(angle) * factor)
            points.append(point)
        return points
    
    def check_collision_with_mouse_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_position = pygame.Vector2(mouse_pos[0], mouse_pos[1])
        if self.position.distance_to(mouse_position) <= self.outer_radius:
            return True
        return False

    def update(self):
        if self.check_collision_with_mouse_hover():
            self.color = "white"
        else:
            self.color = self.initial_color

    def update_center(self):
        #self.center = self.map.coo_to_real_pos(self.coo)
        self.center = self.map.coo_to_real_pos_centered(self.coo)
        self.position = pygame.Vector2(self.center[0], self.center[1])
        self.outer_radius = self.map.tile_outer_radius
        self.inner_radius = self.map.tile_inner_radius
        self.points = self.get_points()
        self.background_points = self.get_background_points()

    def get_self_dict(self):
        return {"coo":self.coo, "type":None, "resource":None, "unit":None, "owner":None, "building":None}

    def draw_background(self):
        #self.update()
        pygame.draw.polygon(self.game.screen, self.background_color, self.background_points)

    def draw_tile(self):
        self.update()
        pygame.draw.polygon(self.game.screen, self.color, self.points)

class Map:
    def __init__(self, game):
        self.game = game
        self.reset()
        self.tiles = []
        self.tiles_coo = set()
        self.update_tile_size()
        self.layer_number = 15

    def reset(self):
        self.tiles_columns = TILES_COLUMNS
        self.tiles_lines = TILES_LINES

        self.tile_horizontal_space = self.game.w / self.tiles_columns
        self.tile_vertical_space = (self.tile_horizontal_space / math.sqrt(3)) * (3/2)
        self.tile_outer_radius = round(self.tile_horizontal_space / 2) # = cercle qui passe par milieu des cotés de l haxagone
        self.tile_inner_radius = round(self.tile_vertical_space / 2) # = cercle qui passe par les sommets de l hexagone
        
        self.tile_number_factor = TILE_NUMBER_FACTOR
        self.last_tile_number_factor = self.tile_number_factor
        self.camera_center = self.add_decalage([self.tiles_columns//2, self.tiles_lines//2])
        self.camera_diff = [0, 0]
        self.camera_movement = [0, 0]

    def add_decalage(self, coo):
        col = coo[0] + (coo[1] % 2) / 2
        row = coo[1]
        return (col, row)

    def remove_decalage(self, coo):
        q = coo[0] - (coo[1] % 2) / 2
        r = coo[1]
        return (q, r)
    
    def coo_to_real_pos(self, coo):
        coo = self.add_decalage(coo)
        x = coo[0] * (self.tile_horizontal_space)
        y = coo[1] * (self.tile_vertical_space)
        #return (x, y)
        return (round(x), round(y))
    
    def coo_to_real_pos_centered(self, coo):
        coo = self.add_decalage(coo)
        relative_x = coo[0] - self.camera_center[0]
        relative_y = coo[1] - self.camera_center[1]
        x = (self.game.w / 2) + (relative_x * self.tile_horizontal_space)
        y = (self.game.h / 2) + (relative_y * self.tile_vertical_space)
        #return (x, y)
        return (round(x), round(y))

    def real_pos_to_coo(self, real_pos):
        x = real_pos[0] / (self.tile_horizontal_space)
        y = real_pos[1] / (self.tile_vertical_space)
        result = self.remove_decalage((x, y))
        return [round(result[0]), round(result[1])]
    
    def real_pos_to_coo_centered(self, real_pos):
        center = self.coo_to_real_pos_centered(self.camera_center)
        x = real_pos[0] - (self.game.w / 2)
        y = real_pos[1] - (self.game.h / 2)
        relative_x = (x / self.tile_horizontal_space) + center[0]
        relative_y = (y / self.tile_vertical_space) + center[1]
        result = self.remove_decalage((relative_x, relative_y))
        return [round(result[0]), round(result[1])]
    
    def find_neighbors(self, coo):
        parity = coo[1] % 2
        neighors = [
                    [(coo[0]+1, coo[1]), (coo[0], coo[1]+1), (coo[0]-1, coo[1]+1), (coo[0]-1, coo[1]), (coo[0]-1, coo[1]-1), (coo[0], coo[1]-1)],
                    [(coo[0]+1, coo[1]), (coo[0]+1, coo[1]+1), (coo[0], coo[1]+1), (coo[0]-1, coo[1]), (coo[0], coo[1]-1), (coo[0]+1, coo[1]-1)]
                    ]
                    # dans le sens des aiguilles d une montre en partant du voisin à droite
        return neighors[parity] # comme les hexagones sont décalés 1 ligne sur 2, les coordonnées des voisins sont différents si le numero de la ligne est pair ou impair
    
    def hexa_grid(self, w, h):
        for y in range(h):
            for x in range(w):
                #hexa = Tile(self.game, (x, y), self.coo_to_real_pos((x, y)), self.tile_inner_radius, self.tile_outer_radius)
                hexa = Tile(self.game, (x, y), self.coo_to_real_pos_centered((x, y)), self.tile_inner_radius, self.tile_outer_radius)
                self.tiles.append(hexa)
                self.tiles_coo.add((x, y))
        print(self.tiles_coo)
    
    def specific_tiles(self, coo_list):
        for coo in coo_list:
            #self.tiles.append(Tile(self.game, coo, self.coo_to_real_pos(coo), self.tile_inner_radius, self.tile_outer_radius))
            self.tiles.append(Tile(self.game, coo, self.coo_to_real_pos_centered(coo), self.tile_inner_radius, self.tile_outer_radius))
            self.tiles_coo.add(coo)

    def layers(self, layers_number):
        coo_list = [set()] # coo_list et une liste de plusieurs sets, chacun correspond à une "layer"
        coo_list[0].add((self.tiles_columns//2, self.tiles_lines//2))
        total_tiles = set()
        total_tiles.update(coo_list[0])
        while len(coo_list) < layers_number:
            coo_list.append(set())
            for coo in coo_list[-2]:
                neighbors = set(self.find_neighbors(coo))
                coo_list[-1].update(neighbors - total_tiles)# ajoute les coo qui sont dans neighbors et qui ne sont pas dans total_tiles, 
                                                            # -> permet de ne pas avoir plusieurs fois les memes coordonnées dans differentes "layers" de coo_list
                                                            # -> utile si pour plus tard on veut seulement les tiles d une certaine layer et pour ne pas chercher des voisins déjà cherchés
                total_tiles.update(neighbors)
        self.tiles_coo.update(total_tiles)
        self.load_from_save() # convertit coo en tiles empty

    def load_tiles_from_coo(self):
        self.tiles = []
        for coo in self.tiles_coo:
            #self.tiles.append(Tile(self.game, coo, self.coo_to_real_pos(coo), self.tile_inner_radius, self.tile_outer_radius))
            self.tiles.append(Tile(self.game, coo, self.coo_to_real_pos_centered(coo), self.tile_inner_radius, self.tile_outer_radius))

    def generate_map(self):
        self.reset()
        self.tiles = []
        self.tiles_coo = set()
        self.layers(self.layer_number)

    def load_from_save(self, coo_list=[]):
        if coo_list != []:
            self.tiles_coo = coo_list
        self.load_tiles_from_coo()

    def update_tile_size(self):
        self.tiles_columns = round(16 * self.tile_number_factor)
        self.tiles_lines = round(self.game.h / self.tile_vertical_space)
        self.tile_horizontal_space = self.game.w / self.tiles_columns
        self.tile_vertical_space = (self.tile_horizontal_space / math.sqrt(3)) * (3/2)
        self.tile_outer_radius = round(self.tile_horizontal_space / 2) # = cercle qui passe par milieu des cotés de l haxagone
        self.tile_inner_radius = round(self.tile_vertical_space / 2) # = cercle qui passe par les sommets de l hexagone

        for tile in self.tiles:
            tile.update_center()
        self.last_tile_number_factor = self.tile_number_factor

    def zoom_camera(self, event):
        if self.game.ui.page == 5: # pour ne pas changer la taille de la map si on ne la voit pas (donc si on n est pas sur game_page() )
            if self.game.ui.button_handler.pause:
                return
            amount = event.dict["precise_y"]
            if self.tile_number_factor + amount / CHANGING_SIZE_SPEED >= MIN_FACTOR and self.tile_number_factor + amount / CHANGING_SIZE_SPEED <= MAX_FACTOR:
                self.tile_number_factor += amount / CHANGING_SIZE_SPEED
            elif self.tile_number_factor + amount / CHANGING_SIZE_SPEED <= MIN_FACTOR:
                self.tile_number_factor = MIN_FACTOR
            elif self.tile_number_factor + amount / CHANGING_SIZE_SPEED >= MAX_FACTOR:
                self.tile_number_factor = MAX_FACTOR

    def move_camera(self, keys):
        if self.game.ui.page == 5:
            if self.game.ui.button_handler.pause:
                return
            speed = round(0.5 * self.tile_number_factor)
            if speed < 1:
                speed = 1
            if keys[pygame.K_d]:
                self.camera_movement[0] += speed
            elif keys[pygame.K_q]:
                self.camera_movement[0] -= speed
            if keys[pygame.K_s]:
                self.camera_movement[1] += speed
            elif keys[pygame.K_z]:
                self.camera_movement[1] -= speed

    def update_camera(self):
        if self.camera_movement != [0, 0]:
            new_center = [self.camera_center[0] + self.camera_movement[0], self.camera_center[1] + self.camera_movement[1]]
            new_real_center = self.coo_to_real_pos(new_center)
            if new_real_center[0] > 0 and new_real_center[0] < self.game.w * (MAX_FACTOR / self.tile_number_factor) and new_real_center[1] > 0 and new_real_center[1] < self.game.h * (MAX_FACTOR / self.tile_number_factor):
                self.camera_center = new_center
                self.camera_diff = [self.camera_diff[0] + self.camera_movement[0], self.camera_diff[1] + self.camera_movement[1]]
                self.update_tile_size()
                self.game.ui.update_center_animated_sea()
        self.camera_movement = [0, 0]

    def draw_tiles(self):
        if self.last_tile_number_factor != self.tile_number_factor:
            self.update_tile_size()
        if self.game.ui.page == 5:
            for tile in self.tiles:
                tile.draw_background()
            for tile in self.tiles:
                tile.draw_tile()

# idees generation map :
# - idee 1
#       - options à la création (frequence de certains types de tiles, frequence de certains types de ressources...)
#       - differents types de tiles
#       - probabilité de spawn pour chaque type de tiles
#       - avec cette probabilité je decide le nombre de "biomes" pour chaque type de tiles
#       - pour la taille de chaque biome, transformer les tiles voisines de l origine du biome en le type du biome selon une probabilité
#       - reduire cette probabilité à chaque nouvelle tile pour le biome (et si 2 ou 3 échecs d'affilée, arreter d expandre le biome)
#       - pour eviter qu un biome en remplace un autre, donner une priorité (plain > water, par exemple)
#
#       - types de tiles (chacune avec ressource de base): empty, plain (food x2), water (water + food), mountain (rock), forest (wood + food)
#       - ressources strategiques (et les biomes compatibles + repartition par biome): horses (plain 1), iron (mountain 1), mana_cristals (mountain 0.7, forest 0.2, plain 0.1), 
#       - buildings : city_center, barracks, farm, lumberjack, fisherman, quarry, mana_extractor          + (a decider : biomes compatibles)
