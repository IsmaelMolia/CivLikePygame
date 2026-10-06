import pygame
from random import randint
from constants import *

class Unit:
    def __init__(self, game, tile_linked, owner):
        self.game = game
        self.tile_linked = tile_linked
        
        self.owner = owner

        self.initial_image = pygame.surface.Surface((self.tile_linked.inner_radius, self.tile_linked.inner_radius))
        self.create()
        self.update_unit()

    def load_image(self):
        try:
            self.initial_image = pygame.image.load(UNITS_FILEPATHS[self.name])
        except: # si self.name n est pas dans UNITS_FILEPATHS ou si la valeur renvoyée n est pas un bon path
            pass

    #def create(self, name="unit", movement=0, damage=0, hp=1, size_constant=1):
    def create(self, name="unit"):
        self.name = name
        self.stats = UNITS_STATS[name]
        #self.max_movement = movement
        self.max_movement = self.stats["movement"]
        self.current_movement = self.max_movement
        #self.damage = damage
        self.damage = self.stats["damage"]
        #self.max_hp = hp
        self.max_hp = self.stats["hp"]
        self.current_hp = self.max_hp

        self.ressource_income = UNITS_INCOME[self.name] # pour les buildings (avec certaines exceptions peut etre ?)
        self.ressource_outcome = UNITS_UPKEEP_COST[self.name]
        self.prod = self.stats["prod"]

        #self.size_constant = size_constant
        self.size_constant = self.stats["size_constant"]
        self.load_image()

    def get_unit_data(self):
        return (self.name, self.tile_linked.coo, self.current_hp, self.current_movement)

    def load_unit_id(self, unit_data):
        #self.name = unit_data[0] # inutile ?
        #self.owner = unit_data[1] # aussi inutile ? # car deja fait dans le __init__
        self.current_hp = unit_data[1]
        self.current_movement = unit_data[2]

    def update_unit(self):
        size = self.tile_linked.inner_radius * self.size_constant
        self.pos = [self.tile_linked.center[0] - size // 2, self.tile_linked.center[1] - size // 2]
        self.image = pygame.transform.scale(self.initial_image, (size, size))
    
    def select_unit(self):
        pass

    def path_finding(self):
        pass

    def move(self, tile): # actuellement ne marche que pour les deplacements de 1 case
        if tile == None: # pas censé arriver, mais au cas où
            return 
        
        neighbors = self.game.map.return_neighbors_tiles(self.tile_linked)
        if tile in neighbors:
            if (tile.unit == None) and (self.current_movement >= TILES_MOVEMENT_COST[tile.type]) and (tile.type not in UNITS_TILES_NOT_ALLOWED[self.name]):
                self.current_movement -= TILES_MOVEMENT_COST[tile.type]
                self.tile_linked.unit = None # on retire l unit de l ancienne case
                self.tile_linked = tile # on se lie à la nouvelle case
                tile.unit = self # on se définit comme l unit de la nouvelle case
                
                self.game.map.selected_tile = tile
                self.game.ui.button_handler.look_selected_tile(self.game.map.selected_tile) # pour update la tile sélectionnée

            elif (tile.unit != None) and (tile.unit.owner != self.owner):
                self.attack(tile.unit)

    def death(self):
        self.tile_linked.unit = None
        self.tile_linked = None
        self.game.map.player_handler.players[self.owner].units_owned.remove(self) # temporaire, bugs

    def attack(self, other):
        other.current_hp -= self.damage
        self.current_hp -= other.damage
        
        if other.current_hp <= 0:
            #other.tile_linked.unit = None # pas besoin ?
            self.tile_linked = other.tile_linked
            self.tile_linked.unit = self
            other.death()

        if self.current_hp <= 0:
            self.death()

        self.game.ui.page_handler.reload_page()

    def special_action(self):
        print("no special action")

    def draw_unit(self):
        self.game.screen.blit(self.image, self.pos)

    def draw_highlighted_unit(self, ennemy=False): # pour l unit de self.game.map.selected_tile (pas très optimisé :/)
        size = self.tile_linked.inner_radius * self.size_constant
        #image = pygame.image.load(f"{CURSOR_FILEPATH}/look_a.png")
        image = pygame.image.load(f"{CURSOR_FILEPATH}/look_a_red.png")
        if not ennemy:
            #image = pygame.image.load(f"{CURSOR_FILEPATH}/arrow_s.png")
            image = pygame.image.load(f"{CURSOR_FILEPATH}/arrow_s_green.png")
        image = pygame.transform.scale(image, (size, size))
        pos_image = [self.tile_linked.center[0] - size // 2, self.tile_linked.center[1] - self.tile_linked.inner_radius * 2]
        
        self.draw_unit()
        self.game.screen.blit(image, pos_image)

class Settler(Unit):
    def __init__(self, game, tile_linked, owner):
        super().__init__(game, tile_linked, owner)
        
        #self.create(name="settler", movement=3, damage=2, hp=10, size_constant=1.2)
        self.create(name="settler")
        self.update_unit()

    def special_action(self): # create_city
        city = City(self.game, self.tile_linked, self.owner)
        self.tile_linked.building = city
        city.tile_linked = self.tile_linked
        self.tile_linked.owner = self.owner

        self.tile_linked.unit = None
        self.tile_linked = None

        self.game.map.player_handler.players[self.owner].units_owned.remove(self)
        self.game.map.player_handler.players[self.owner].units_owned.append(city)
        
        #self.game.map.player_handler.players[self.owner].tiles_owned.append(city.tile_linked)
        self.game.map.player_handler.players[self.owner].add_tile_owned(city.tile_linked, city.tile_linked)
        if BIG_SPAWN:
            for tile in self.game.map.return_neighbors_tiles(city.tile_linked):
                if tile.owner == None:
                    self.game.map.player_handler.players[self.owner].add_tile_owned(tile, city.tile_linked)
        self.game.map.player_handler.players[self.owner].update_map_tiles_owner()
        self.game.map.player_handler.players[self.owner].update_color_tiles()
        
class City(Unit):
    def __init__(self, game, tile_linked, owner):
        super().__init__(game, tile_linked, owner)

        #self.create(name="city", damage=5, hp=100)
        self.create(name="city")
        self.regional_prod = self.prod # regional_prod est une stat spéciale à City, elle sert à calculer la prod totale des tiles de la ville
        #self.food_expansion = (0, BASE_EXPANSION_FOOD_NEEDED) # aussi une stat speciale à City
        self.food_expansion = [0, BASE_EXPANSION_FOOD_NEEDED] # aussi une stat speciale à City (list car bugs quand tuple)
        self.update_unit()

    def calculate_regional_prod(self, regional_tiles):
        self.regional_prod = 0 # on met la prod de la ville à 0
        for tile in regional_tiles:
            for r in NORMAL_RESSOURCES[tile.type]:
                self.regional_prod += PROD_PER_RESSOURCE[r] # on ajoute la prod de chaque ressource (pour l instant seulement les ressources normales)
            if tile.building != None:
                self.regional_prod += tile.building.prod # on ajoute la prod des buildings

    def calculate_local_food_income(self, regional_tiles):
        food = 0
        for tile in regional_tiles:
            for r in NORMAL_RESSOURCES[tile.type]:
                if r == "food":
                    food += 1
        return food
    
    def expand(self, regional_tiles):
        if len(regional_tiles) >= MAXIMUM_TILES_PER_CITY:
            return

        possible_new_tiles = []
        for tile in regional_tiles:
            for neighbor in self.game.map.return_neighbors_tiles(tile):
                if (neighbor.owner == None) and (neighbor not in possible_new_tiles):
                    possible_new_tiles.append(neighbor)
        if possible_new_tiles == []:
            return
        
        new_tile = possible_new_tiles[randint(0, len(possible_new_tiles) - 1)]
        self.game.map.player_handler.players[self.owner].add_tile_owned(new_tile, self.tile_linked)
        self.game.map.player_handler.players[self.owner].update_map_tiles_owner()
        self.game.map.player_handler.players[self.owner].update_color_tiles()
        
        self.food_expansion[0] -= self.food_expansion[1]
        self.food_expansion[1] += FOOD_NEED_ADDED_PER_NEW_TILE

    def calculate_expansion(self, regional_tiles):
        food_income = self.calculate_local_food_income(regional_tiles)
        self.food_expansion[0] += food_income
        if self.food_expansion[0] >= self.food_expansion[1]:
            self.expand(regional_tiles)

