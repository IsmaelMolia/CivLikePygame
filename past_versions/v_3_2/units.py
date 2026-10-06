import pygame
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

    def create(self, name="unit", movement=0, damage=0, range=1, hp=1, size_constant=1):
        self.name = name
        self.max_movement = movement
        self.current_movement = self.max_movement
        self.damage = damage
        self.range = range
        self.max_hp = hp
        self.current_hp = self.max_hp

        self.ressource_income = UNITS_INCOME[self.name] # pour les buildings (avec certaines exceptions peut etre ?)
        self.ressource_outcome = UNITS_UPKEEP_COST[self.name]

        self.size_constant = size_constant
        self.load_image()

        self.descriptions = UNITS_DESCRIPTIONS[self.name] # pour side_page INSPECT

    def get_unit_id(self):
        return (self.name, self.owner, self.current_hp, self.current_movement)

    def load_unit_id(self, unit_id):
        #self.name = unit_id[0] # inutile ?
        #self.owner = unit_id[1] # aussi inutile ? # car deja fait dans le __init__
        self.current_hp = unit_id[2]
        self.current_movement = unit_id[3]

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
        if (tile in neighbors) and (tile.unit == None) and (self.current_movement >= TILES_MOVEMENT_COST[tile.type]) and (tile.type not in UNITS_TILES_NOT_ALLOWED[self.name]):
            self.current_movement -= TILES_MOVEMENT_COST[tile.type]
            self.tile_linked.unit = None # on retire l unit de l ancienne case
            self.tile_linked = tile # on se lie à la nouvelle case
            tile.unit = self # on se définit comme l unit de la nouvelle case
            
            self.game.map.selected_tile = tile
            self.game.ui.button_handler.look_selected_tile(self.game.map.selected_tile) # pour update la tile sélectionnée

        elif (tile.unit != None) and (tile.unit.owner != self.owner):
            self.attack(tile.unit)

    def death(self):
        pass

    def attack(self, other):
        other.current_hp -= self.damage
        self.current_hp -= other.damage
        
        if other.current.hp <= 0:
            self.tile_linked.unit = None
            self.tile_linked = other.tile_linked
            self.tile_linked.unit = self
            self.game.map.player_handler.players[other.owner].units_owned.remove(other)

        if self.current_hp <= 0:
            self.tile_linked.unit = None
            self.tile_linked = None
            self.game.map.player_handler.players[self.owner].units_owned.remove(self)

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
        
        self.create(name="settler", movement=3, damage=2, hp=10, size_constant=1.2)
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
        
        self.game.map.player_handler.players[self.owner].tiles_owned.append(city.tile_linked)
        self.game.map.player_handler.players[self.owner].update_color_tiles()
        
class City(Unit):
    def __init__(self, game, tile_linked, owner):
        super().__init__(game, tile_linked, owner)

        self.create(name="city", damage=5, hp=100)
        self.update_unit()

# faire une classe Unit et les autres types d'units seront en hériteront (seront ses enfants) ?
# voir buildings comme des units ? (avec 0 mouvement et production ressources ?)
