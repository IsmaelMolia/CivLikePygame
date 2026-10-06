import pygame
import math
from random import randint
from constants import *
#from units import *
from players import *

class Tile:
    def __init__(self, game, coo, center, inner_radius, outer_radius, type="plain", strategic_ressources=[], owner=None, building=None, unit=None):
        self.game = game
        self.map = self.game.map

        self.coo = coo
        self.center = center
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        
        self.type = type
        self.color = TILES_COLORS[self.type]
        self.initial_color = self.color
        self.background_color = TILE_BACKGROUND_COLOR
        self.initial_background_color = self.background_color
        self.strategic_ressources = strategic_ressources

        self.owner = owner
        self.building = building
        self.unit = unit
        
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

    def update(self, check_prio=True):
        #self.color = self.initial_color
        self.background_color = self.initial_background_color
        if self.check_collision_with_mouse_hover() and check_prio:
            #self.color = "white"
            self.background_color = "white"
            self.game.map.tile_with_prio = self

    def update_center(self):
        #self.center = self.map.coo_to_real_pos(self.coo)
        self.center = self.map.coo_to_real_pos_centered(self.coo)
        self.position = pygame.Vector2(self.center[0], self.center[1])
        self.outer_radius = self.map.tile_outer_radius
        self.inner_radius = self.map.tile_inner_radius
        self.points = self.get_points()
        self.background_points = self.get_background_points()

        if self.building != None:
            self.building.update_unit()
        if self.unit != None:
            self.unit.update_unit()

        if self.map.vision_modes["ressources"]:
            self.ressources_icons = []
            self.ressources_icons_positions = []
            
            for normal in NORMAL_RESSOURCES[self.type]:
                self.ressources_icons.append(pygame.transform.scale(self.game.ui.page_handler.ressources_icons[normal], (self.inner_radius * RESSOURCE_SIZE, self.inner_radius * RESSOURCE_SIZE)))
            for strategic in self.strategic_ressources:
                self.ressources_icons.append(pygame.transform.scale(self.game.ui.page_handler.ressources_icons[strategic], (self.inner_radius * RESSOURCE_SIZE, self.inner_radius * RESSOURCE_SIZE)))

            for i in range(len(self.ressources_icons)):
                initial_decalage = self.inner_radius * (RESSOURCE_SIZE / 2) # decalage de base pour recentrer l icone
                decalage = self.inner_radius * RESSOURCE_SIZE # decalage maximal vers la droite ou la gauche. ainsi, "self.center[0] - initial_decalage - decalage" est la position la + à droite et "self.center[0] - initial_decalage + decalage" celle la plus à gauche
                interval = decalage * 2 # distance max, de la position la plus à droite à celle la plus à gauche
                space = interval / (len(self.ressources_icons) + 1) # on découpe la distance max en segments selon le nombre d icones. avec "space * (i+1)", on peut ainsi placer chaque icone avce un espace regulier entre elles, de la position la plus à droite à celle la + à gauche
                # pour voir si ce sytseme fonctionne bien, on peut modifier les ressources dans NORMAL_RESSOURCES de constants.py (en mettant "plain":["food", "food", "food", "food", "food", "food"] par exemple)
                
                self.ressources_icons_positions.append((self.center[0] - initial_decalage - decalage + space * (i+1), self.center[1] + self.inner_radius * RESSOURCE_VERTICAL_DECALAGE))

    def get_self_dict(self):
        return {"coo":self.coo, "type":None, "resource":None, "unit":None, "owner":None, "building":None}

    #def draw_background(self, update=True, fog_of_war=False):
    #if update:
        #self.update()
    def draw_background(self, check_prio=True, fog_of_war=False, specific_color=None):
        self.update(check_prio) # comme ça, si pause == True, on met check_prio en False et toutes les backgrounds de tiles repprennent leur couleur normale

        if fog_of_war:
            if not self.game.map.tile_with_prio == self:
                pygame.draw.polygon(self.game.screen, self.map.fog_of_war_background_color, self.background_points)
            else:
                pygame.draw.polygon(self.game.screen, self.background_color, self.background_points)
        elif specific_color != None:
            if not self.game.map.tile_with_prio == self:
                pygame.draw.polygon(self.game.screen, self.map.fog_of_war_background_color, self.background_points)
            else:
                pygame.draw.polygon(self.game.screen, specific_color, self.background_points)
        else:
            pygame.draw.polygon(self.game.screen, self.background_color, self.background_points)

    def draw_tile(self, fog_of_war=False, specific_color=None):
        if fog_of_war:
            pygame.draw.polygon(self.game.screen, self.map.fog_of_war_tile_color, self.points)
            return
        elif specific_color != None:
            pygame.draw.polygon(self.game.screen, specific_color, self.points)
        else:
            pygame.draw.polygon(self.game.screen, self.color, self.points)
        
        if self.building != None:
            self.building.draw_unit()
        if self.unit != None:
            self.unit.draw_unit()

    def draw_ressources(self, fog_of_war=False):
        if fog_of_war:
            return
        for i in range(len(self.ressources_icons)):
            self.game.screen.blit(self.ressources_icons[i], self.ressources_icons_positions[i])

class Map:
    def __init__(self, game):
        self.game = game
        
        self.reset()
        self.tiles = []
        self.tiles_coo = set()
        self.tile_with_prio = None
        self.selected_tile = None
        self.last_selected_tile = None
        
        self.update_tile_size()
        self.layer_number = MAX_LAYERS//4
        self.get_tiles_frequences()

        self.fog_of_war = False
        self.fog_of_war_tile_color = FOG_OF_WAR_TILE_COLOR
        self.fog_of_war_background_color = FOG_OF_WAR_BACKGROUND_COLOR
        self.player_handler = PlayerHandler(self.game)

    def get_tiles_frequences(self):
        frequences = TILES_PROBABILITIES
        self.tiles_frequences = {}
        self.tiles_frequences["empty"] = frequences["empty"]
        self.tiles_frequences["plain"] = frequences["plain"]
        self.tiles_frequences["water"] = frequences["water"]
        self.tiles_frequences["mountain"] = frequences["mountain"]
        self.tiles_frequences["forest"] = frequences["forest"]
        self.tiles_frequences["hill"] = frequences["hill"]

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
        self.initial_camera_center = self.camera_center
        self.camera_diff = [0, 0]
        self.camera_movement = [0, 0]

        self.vision_modes = {"empire":False, "ressources":False}

    def change_vision_mode(self, modes, bools):
        if self.game.ui.page_handler.page == 5:
            for i in range(len(modes)):
                self.vision_modes[modes[i]] = bools[i]
            
            if self.vision_modes["ressources"]:
                self.update_tile_size()

    def change_fog_of_war(self):
        self.fog_of_war = not self.fog_of_war
        if self.game.ui.page_handler.state_side_pages["TILE"]:
            self.game.ui.button_handler.update_text_side_page("TILE")

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
                    # dans le sens des aiguilles d une montre en partant du voisin à droite (systeme odd-r dans https://www.redblobgames.com/grids/hexagons/)
        return neighors[parity] # comme les hexagones sont décalés 1 ligne sur 2, les coordonnées des voisins sont différents si le numero de la ligne est pair ou impair
    
    def find_possible_neighbors(self, coo): # actuellement, seulement utile pour tiles_seen
        real_neighbors = []
        possible_neighbors = self.find_neighbors(coo)
        for tile in self.tiles:
            if tile.coo in possible_neighbors:
                real_neighbors.append(tile.coo)
        return real_neighbors
    
    def return_neighbors_tiles(self, tile):
        neighbors = []
        possible_neighbors = self.find_neighbors(tile.coo)
        for tile in self.tiles:
            if tile.coo in possible_neighbors:
                neighbors.append(tile)
        return neighbors
    
    def return_empty_neighbors_tiles(self, tile, empty_tiles):
        neighbors = []
        possible_neighbors = self.find_neighbors(tile.coo)
        for n in possible_neighbors:
            if n in empty_tiles:
                neighbors.append(n)
        return neighbors
    
    def hexa_grid(self, w, h):
        for y in range(h):
            for x in range(w):
                #hexa = Tile(self.game, (x, y), self.coo_to_real_pos((x, y)), self.tile_inner_radius, self.tile_outer_radius)
                hexa = Tile(self.game, (x, y), self.coo_to_real_pos_centered((x, y)), self.tile_inner_radius, self.tile_outer_radius)
                self.tiles.append(hexa)
                self.tiles_coo.add((x, y))
        #print(self.tiles_coo)

    def create_proba(self):
        intervals = {}
        total = 0
        #for t, p in TILES_PROBABILITIES.items():
        for t, p in self.tiles_frequences.items():
            intervals[t] = [total, total+p]
            total += p
        return total, intervals
    
    def get_tiles_frequences_percentages(self):
        total_proba, intervals = self.create_proba()
        percentages = {}
        for t, p in self.tiles_frequences.items():
            if p < 1:
                percentages[t] = 0
                continue
            percentages[t] = round((p / total_proba) * 100)
        return percentages, total_proba
    
    def get_settler_possibilities(self):
        possibilities = []
        for tile in self.tiles:
            if (tile.type == "plain" or tile.type == "hill") and (tile.unit == None): # derniere condition utile dans le cas où plusieurs settlers sont créés
                possibilities.append(tile)
        return possibilities

    def random_tiles(self):
        total_proba, intervals = self.create_proba()
        #print(total_proba, intervals)
        self.tiles = []
        for coo in self.tiles_coo:
            n = randint(0, total_proba)
            for t, p in intervals.items():
                #if n >= p[0] and n < p[1]:
                if n < p[1]:
                    type = t
                    break
            self.tiles.append(Tile(self.game, coo, self.coo_to_real_pos_centered(coo), self.tile_inner_radius, self.tile_outer_radius, type))

        for tile in self.tiles:
            if (tile.type == "plain") or (tile.type == "hill"):
                return
        r = randint(0, len(self.tiles) - 1)
        coo = self.tiles[r].coo
        self.tiles.pop(r)
        self.tiles.append(Tile(self.game, coo, self.coo_to_real_pos_centered(coo), self.tile_inner_radius, self.tile_outer_radius, "plain"))
        # si jamais aucun spawn pour un settler 

    def seed_generation_v1(self, biomes, empty_tiles):
        while len(empty_tiles):
            new_biomes = biomes.copy() # va causer des duplications de biomes, mais comme une seule tile aleatoire est verifiee par biome et que si elle n a pas de voisins son biome est supprimé, 
                                       # on ne peut pas faire "new_biomes = []"... mais normalement probleme réglé dans seed_generation_v2() :)
            for biome in biomes:
                r = randint(0, len(biome) - 1)
                chosen_tile = biome[r][0]
                tile_type = biome[r][1]
                neighbors_coo = self.return_empty_neighbors_tiles(chosen_tile, empty_tiles)
                if len(neighbors_coo):
                    added_tile_coo = neighbors_coo[randint(0, len(neighbors_coo) - 1)]
                    added_tile = Tile(self.game, added_tile_coo, self.coo_to_real_pos_centered(added_tile_coo), self.tile_inner_radius, self.tile_outer_radius, tile_type)
                    biome.append((added_tile, tile_type))
                    self.tiles.append(added_tile)
                    for coo in empty_tiles:
                        if coo == added_tile_coo:
                            empty_tiles.remove(coo)
                            break
                    new_biomes.append(biome)
            biomes = new_biomes.copy()

    def seed_generation_v2(self, biomes, empty_tiles):
        expanding_biomes = biomes.copy()

        while len(empty_tiles):
            new_expanding_biomes = []
            expanding_biomes_with_expanding_tiles_only = []
            
            # on garde seulement les tiles qui ont des neighbors
            for biome in expanding_biomes:
                new_biome = []
                for tile in biome:
                    neighbors_coo = self.return_empty_neighbors_tiles(tile[0], empty_tiles)
                    if len(neighbors_coo):
                        new_biome.append(tile)
                if len(new_biome):
                    expanding_biomes_with_expanding_tiles_only.append(new_biome)
            expanding_biomes = expanding_biomes_with_expanding_tiles_only.copy()

            # si jamais plus aucun expanding_biome (ne devrait pas arriver si il y a encore des tiles dans empty_tiles, mais juste au cas ou)
            if not len(expanding_biomes):
                break
        
            for biome in expanding_biomes:
                
                # tile aleatoire
                r = randint(0, len(biome) - 1)
                chosen_tile = biome[r][0]
                tile_type = biome[r][1]

                if len(biome) >= BIOMES_SIZES_INTERVALS[tile_type][1]: # pour ne pas depasser taille limite
                    continue

                # neighbor aleatoire
                neighbors_coo = self.return_empty_neighbors_tiles(chosen_tile, empty_tiles)
                if not neighbors_coo:
                    continue
                added_tile_coo = neighbors_coo[randint(0, len(neighbors_coo) - 1)]
                added_tile = Tile(self.game, added_tile_coo, self.coo_to_real_pos_centered(added_tile_coo), self.tile_inner_radius, self.tile_outer_radius, tile_type)
                
                # ajout du neighbor choisi
                biome.append((added_tile, tile_type))
                self.tiles.append(added_tile)
                new_expanding_biomes.append(biome)

                # update empty_tiles (retirer added_tile)
                for coo in empty_tiles:
                    if coo == added_tile_coo:
                        empty_tiles.remove(coo)
                        break
                
            expanding_biomes = new_expanding_biomes.copy()

    def seed_generation_v3(self, biomes, empty_tiles):
        total_tiles = {} # juste pour avoir plus de stats :)
        for biome in biomes:
            if biome[0][1] in total_tiles.keys():
                total_tiles[biome[0][1]] += 1
            else:
                total_tiles[biome[0][1]] = 1

        total_proba, intervals = self.create_proba()
        biomes_max_sizes = {}
        total_tiles_number = len(self.tiles_coo)
        for key, value in self.tiles_frequences.items():
            if value < 1:
                continue
            biomes_max_sizes[key] = round(total_tiles_number * (value / total_proba))

        expanding_biomes = biomes.copy()

        while len(empty_tiles):
            new_biomes = []

            # si jamais plus aucun expanding_biome (ne devrait pas arriver si il y a encore des tiles dans empty_tiles, mais juste au cas ou)
            if not len(expanding_biomes):
                if "plain" not in total_tiles.keys(): # dans le rare cas où il n y a pas eu de seed plain (c est deja arrivé 1 fois :/ )
                    total_tiles["plain"] = 0
                for empty_tile in empty_tiles:
                    # filler plain tiles, pour ne pas avoir de trous
                    self.tiles.append(Tile(self.game, empty_tile, self.coo_to_real_pos_centered(empty_tile), self.tile_inner_radius, self.tile_outer_radius, "plain"))
                    total_tiles["plain"] += 1
                break
                
            for biome in expanding_biomes:

                tile_type = biome[0][1]

                # on garde seulement les tiles qui ont des neighbors
                expanding_tiles = []
                for tile in biome:
                    neighbors_coo = self.return_empty_neighbors_tiles(tile[0], empty_tiles)
                    if len(neighbors_coo):
                        expanding_tiles.append(tile)
                
                # on skip le biome si il ne peut pas s expandre et 2 autres conditions pour ne pas depasser limite de taille
                if (not len(expanding_tiles)) or (len(biome) >= BIOMES_SIZES_INTERVALS[tile_type][1]) or (total_tiles[tile_type] >= biomes_max_sizes[tile_type]):
                    continue
                
                # tile aleatoire
                r = randint(0, len(expanding_tiles) - 1)
                chosen_tile = expanding_tiles[r][0]

                # neighbor aleatoire
                neighbors_coo = self.return_empty_neighbors_tiles(chosen_tile, empty_tiles)
                #if not neighbors_coo: # utile si par exemple des tiles A et B on un neighbor commun, et A s'expand sur ce neighbor, et B n a plus de neighbor
                    #continue
                added_tile_coo = neighbors_coo[randint(0, len(neighbors_coo) - 1)]
                added_tile = Tile(self.game, added_tile_coo, self.coo_to_real_pos_centered(added_tile_coo), self.tile_inner_radius, self.tile_outer_radius, tile_type)
                
                # ajout du neighbor choisi
                biome.append((added_tile, tile_type))
                self.tiles.append(added_tile)
                new_biomes.append(biome)
                total_tiles[tile_type] += 1

                # update empty_tiles (retirer added_tile)
                for coo in empty_tiles:
                    if coo == added_tile_coo:
                        empty_tiles.remove(coo)
                        break
                
            expanding_biomes = new_biomes.copy()
        #print(f"maximum size per biome : {biomes_max_sizes}")
        if PRINT_TOTAL_TILES:
            print(f"total number of tiles : {total_tiles}")

    def organic_tiles(self):
        total_proba, intervals = self.create_proba()
        self.tiles = []
        empty_tiles = list(self.tiles_coo.copy())

        biomes_size = {}
        for key, value in BIOMES_SIZES_INTERVALS.items():
            biomes_size[key] = [value[0], value[1], (value[0] + value[1]) // 2]

        biomes_seeds_number = {}
        total_tiles = len(self.tiles_coo)
        for key, value in self.tiles_frequences.items():
            if value < 1:
                continue
            biomes_seeds_number[key] = round((total_tiles * (value / total_proba)) / biomes_size[key][2])
            # d abord on trouve le nombre de tiles qui seront d un certain type (ex : avec 200 tiles et 30% water, 60 tiles water)
            # puis on divise par la taille moyenne d un biome de ce type pour trouver le nombre de seeds (ex : 60 tiles, taille moyenne du biome 6, donc 10 seeds)
        #print(biomes_seeds_number)

        existant_biomes = 0
        for key, value in biomes_seeds_number.items():
            if value != 0:
                existant_biomes += 1
                break
        if existant_biomes == 0: 
            self.random_tiles()
            return
        # cette partie est pour verifier si le nombre total de seeds et de 0 (car map trop petite par rapport à taille biomes), et dans ce cas faire une generation random

        #biomes_seeds = {}
        biomes = [] # liste de biomes (chaque biome = liste de tiles)
        for key, value in biomes_seeds_number.items():
            seeds = []
            for i in range(value):
                n = randint(0, len(empty_tiles) - 1)
                random_empty_tile = empty_tiles[n]
                empty_tiles.pop(n)
                tile = Tile(self.game, random_empty_tile, self.coo_to_real_pos_centered(random_empty_tile), self.tile_inner_radius, self.tile_outer_radius, key)
                self.tiles.append(tile)
                seeds.append(tile)
                biomes.append([(tile, key)])
            #biomes_seeds[key] = seeds
        # actuellement biomes_seeds inutile, peut etre a utiliser plus tard ?

        #for empty_tile in empty_tiles:
            #self.tiles.append(Tile(self.game, empty_tile, self.coo_to_real_pos_centered(empty_tile), self.tile_inner_radius, self.tile_outer_radius, "empty"))

        #self.seed_generation_v1(biomes, empty_tiles)
        #self.seed_generation_v2(biomes, empty_tiles)
        self.seed_generation_v3(biomes, empty_tiles)

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

    def generate_map(self):
        #self.reset()
        self.reset_camera()
        self.tiles = []
        self.tiles_coo = set()
        self.layers(self.layer_number)
        #print("done 1")
        #self.random_tiles()
        self.organic_tiles()
        #print("done 2")
        self.player_handler.initial_players()
        self.focus_camera(self.player_handler.players["1"].units_owned[0].tile_linked)

    def get_tiles(self):
        tiles = []
        for tile in self.tiles:
            tiles.append([tile.coo, tile.type, tile.strategic_ressources])
        return tiles

    def load_from_save(self, tiles):
        self.tiles = []
        for tile in tiles:
            t = Tile(self.game, tile[0], self.coo_to_real_pos_centered(tile[0]), self.tile_inner_radius, self.tile_outer_radius, tile[1], tile[2])
            self.tiles.append(t)
        
        self.tiles_coo = set()
        for coo in tiles:
            self.tiles_coo.add(tuple(coo[0]))

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
        if self.game.ui.page_handler.page == 5: # pour ne pas changer la taille de la map si on ne la voit pas (donc si on n est pas sur game_page() )
            if self.game.ui.page_handler.pause:
                return
            amount = event.dict["precise_y"]
            if self.tile_number_factor + amount / CHANGING_SIZE_SPEED >= MIN_FACTOR and self.tile_number_factor + amount / CHANGING_SIZE_SPEED <= MAX_FACTOR:
                self.tile_number_factor += amount / CHANGING_SIZE_SPEED
            elif self.tile_number_factor + amount / CHANGING_SIZE_SPEED <= MIN_FACTOR:
                self.tile_number_factor = MIN_FACTOR
            elif self.tile_number_factor + amount / CHANGING_SIZE_SPEED >= MAX_FACTOR:
                self.tile_number_factor = MAX_FACTOR
            self.update_camera(True)

    def move_camera(self, keys):
        if self.game.ui.page_handler.page == 5:
            if self.game.ui.page_handler.pause:
                return
            #speed = round(0.2 * self.tile_number_factor * self.tile_number_factor)
            #if speed < 1:
                #speed = 1
            speed = 0.3 * self.tile_number_factor
            if speed > MAX_FACTOR:
                speed = MAX_FACTOR
            if keys[pygame.K_d]:
                self.camera_movement[0] += speed
            elif keys[pygame.K_q]:
                self.camera_movement[0] -= speed
            if keys[pygame.K_s]:
                self.camera_movement[1] += speed
            elif keys[pygame.K_z]:
                self.camera_movement[1] -= speed

    def focus_camera(self, tile):
        self.reset_camera()
        self.camera_movement = [tile.coo[0] - self.initial_camera_center[0], tile.coo[1] - self.initial_camera_center[1]]
        self.tile_number_factor = MIN_FACTOR
        self.update_camera()

    def update_camera(self, force_update=False):
        if( self.camera_movement != [0, 0]) or force_update:
            new_center = [self.camera_center[0] + self.camera_movement[0], self.camera_center[1] + self.camera_movement[1]]
            #if new_center[0] > -self.layer_number and new_center[0] < self.layer_number * 3 and new_center[1] > -self.layer_number and new_center[1] < self.layer_number * 2:
            if new_center[0] > -MAX_LAYERS and new_center[0] < MAX_LAYERS * 2 and new_center[1] > -MAX_LAYERS and new_center[1] < MAX_LAYERS * 2:
                self.camera_center = new_center
                self.camera_diff = [self.camera_diff[0] + self.camera_movement[0], self.camera_diff[1] + self.camera_movement[1]]
                self.update_tile_size()
                self.game.ui.page_handler.update_center_animated_sea()
        self.camera_movement = [0, 0]

    def reset_camera(self):
        self.reset()
        self.update_tile_size()
        self.game.ui.page_handler.update_center_animated_sea()

    def check_if_owned_unit_selected(self):
        if self.selected_tile != None:
            if ((self.selected_tile in self.player_handler.players["1"].tiles_seen) or not self.fog_of_war) and (self.selected_tile.unit != None) and (self.game.ui.page_handler.state_side_pages["CURRENT_UNIT"]):
                return True
        return False
    
    def make_city(self):
        if self.check_if_owned_unit_selected():
            if self.selected_tile.unit.name == "settler":
                self.selected_tile.unit.special_action()
                
                self.player_handler.players["1"].calculate_income_and_outcome() 
                self.game.ui.page_handler.reload_page() # pour update l'UI

    def draw_empire_tiles(self):
        for player in self.player_handler.players.values():
            for city_and_tiles_1 in player.tiles_owned:
                #city_and_tiles_1[0].draw_background(not self.game.ui.page_handler.pause, ((self.fog_of_war) and (not t1 in self.player_handler.players["1"].tiles_seen)))
                for t1 in city_and_tiles_1[1]:
                    t1.draw_background(not self.game.ui.page_handler.pause, ((self.fog_of_war) and (not t1 in self.player_handler.players["1"].tiles_seen)))
            
            for city_and_tiles_2 in player.tiles_owned:
                #city_and_tiles_2[0].draw_tile(((self.fog_of_war) and (not t2 in self.player_handler.players["1"].tiles_seen)))
                for t2 in city_and_tiles_2[1]:
                    t2.draw_tile(((self.fog_of_war) and (not t2 in self.player_handler.players["1"].tiles_seen)))
            # "((self.fog_of_war) and (not tile in self.player_handler.players["1"].tiles_seen))" permet de savoir si la tile est visible (elle ne l est pas seulement si fog_of_war est vrai et qu'elle n'est pas dans les tiles_seen)

        if self.vision_modes["empire"]:
            empire_tiles = [] # les tiles d empire
            for player in self.player_handler.players.values():
                empire_tiles += player.tiles_owned

            for city_and_tiles_3 in empire_tiles:
                #city_and_tiles_3[0].draw_tile(((self.fog_of_war) and (not tile in self.player_handler.players["1"].tiles_seen)), tile.initial_background_color)
                for tile in city_and_tiles_3[1]:
                    tile.draw_tile(((self.fog_of_war) and (not tile in self.player_handler.players["1"].tiles_seen)), tile.initial_background_color)

    def draw_ressources_tiles(self):
        if self.vision_modes["ressources"]:
            for tile in self.tiles:
                tile.draw_ressources(((self.fog_of_war) and (not tile in self.player_handler.players["1"].tiles_seen)))

    def get_color_tile_with_prio(self):
        color_tile = self.tile_with_prio.initial_color

        if self.vision_modes["empire"]: # car pas besoin de calculer tout ça si self.vision_modes["empire"] == False
            empire_tiles = [] # les tiles d empire
            for player in self.player_handler.players.values():
                empire_tiles += player.tiles_owned

            in_empire_tiles = False
            for city_and_tiles in empire_tiles:
                #if city_and_tiles[0] == self.tile_with_prio:
                    #in_empire_tiles = True
                    #break
                for tile in city_and_tiles[1]:
                    if tile == self.tile_with_prio:
                        in_empire_tiles = True
                        break
                if in_empire_tiles:
                    break

            if (in_empire_tiles) and ((self.tile_with_prio in self.player_handler.players["1"].tiles_seen) or (not self.fog_of_war)):
                color_tile = self.tile_with_prio.initial_background_color

        return color_tile

    def draw_tile_with_prio(self):
        if self.tile_with_prio != None:
            self.tile_with_prio.draw_background(not self.game.ui.page_handler.pause, False)
            self.tile_with_prio.draw_tile(((self.fog_of_war) and (not self.tile_with_prio in self.player_handler.players["1"].tiles_seen)), self.get_color_tile_with_prio())
    
    def draw_tile_with_highlighted_unit(self):
        if self.selected_tile != None:
            if self.check_if_owned_unit_selected():
                if self.selected_tile.unit.owner == "1":
                    self.selected_tile.unit.draw_highlighted_unit(False) 
                else:
                    self.selected_tile.unit.draw_highlighted_unit(True) 

    def draw_tiles(self): # vraiment pas optimisé :/ mais bon pas grave :)
        if self.game.ui.page_handler.page == 5:
            self.tile_with_prio = None
            if self.last_tile_number_factor != self.tile_number_factor:
                self.update_tile_size()

            # highlighted_unit > tile_ressources > (tile_with_prio + background_tile_with_prio) > (tiles_empire + backgrounds_empire) > tiles_seen > tiles_fog_of_war > backgrounds_tiles_seen > backgrounds_fog_of_war
            # petit probleme : donc, meme avec le fog_of_war, il est possible de savoir où sont les villes ennemies puisqu elles seront dessinées en priorité (la différence avec les autres tiles fog_of_war est légère mais visible)
            for background_fog_of_war in self.tiles:
                background_fog_of_war.draw_background(not self.game.ui.page_handler.pause, self.fog_of_war)
            
            for background_tiles_seen in self.player_handler.players["1"].tiles_seen:
                background_tiles_seen.draw_background(not self.game.ui.page_handler.pause, False)
            
            for tile_fog_of_war in self.tiles:
                tile_fog_of_war.draw_tile(self.fog_of_war)

            for tile_seen in self.player_handler.players["1"].tiles_seen:
                tile_seen.draw_tile(False)

            self.draw_empire_tiles() # backgrounds_empire puis tiles_empire
            self.draw_tile_with_prio() # background_tile_with_prio puis tile_with_prio
            self.draw_ressources_tiles() # tile_ressources
            self.draw_tile_with_highlighted_unit() # highlighted_unit
            

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
#       - types de tiles (chacune avec ressource de base): empty, plain (food x2), water (food), mountain (rock x2), forest (wood + food), hill (rock)    + gold (avec batiments, faisable sur toutes les tiles)
#       - ressources strategiques (et les biomes compatibles + repartition par biome): horse (plain 1), iron (mountain 1), mana_cristal (mountain 0.7, forest 0.2, plain 0.1)
#       - buildings : city_center, barracks, farm, lumberjack, fisherman, quarry, mana_extractor          + (a decider : biomes compatibles)
