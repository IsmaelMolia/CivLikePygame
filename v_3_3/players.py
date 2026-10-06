from random import randint
import pygame
from units import *
from constants import *

class Player:
    def __init__(self, game, id):
        self.game = game
        self.player_handler = self.game.map.player_handler
        self.id = id
        self.color = TILE_BACKGROUND_COLOR
        
        self.tiles_owned = [] # une liste de sous-listes de la forme "tiles_owned = [[city_1, [tile_1, tile_2, tile_3]], [city_2, [tile_4, tile_5]], ...]"
        self.units_owned = [] # units + buildings
       
        self.ressource_storage = {}
        for ressource_name in RESSOURCES_FILEPATHS.keys():
            self.ressource_storage[ressource_name] = 0 # pour initialiser toutes les ressources à 0
        self.ressource_storage["food"] = 10 # pour commencer avec une nourriture de 10
        self.calculate_income_and_outcome() # pour avoir self.ressource_income
        
        self.tiles_seen = set() # pour le fog of war
        self.tiles_seen_coos = set()

    def get_ressource_storage_to_list(self):
        ressource_list = []
        for key, value in self.ressource_storage.items():
            ressource_list.append((key, value))
        return ressource_list
    
    def get_tiles_owned(self):
        tiles_owned_list = []

        for city_and_tiles in self.tiles_owned:
            tiles_coos = []
            for tile in city_and_tiles[1]:
                tiles_coos.append(tile.coo)
            tiles_owned_list.append([city_and_tiles[0].coo, tiles_coos])
        
        return tiles_owned_list

    def get_units_owned(self):
        units_owned_list = []

        for unit in self.units_owned:
            units_owned_list.append(unit.get_unit_data())

        return units_owned_list

    def load_ressource_storage_to_dict(self, ressource_list):
        self.ressource_storage = {}
        for ressource in ressource_list:
            self.ressource_storage[ressource[0]] = ressource[1]

    def load_tiles_owned(self, tiles_owned_list):
        self.tiles_owned = []

        temporary_tiles_owned = [] # pour creer une liste de la forme [(city_1, tile_1), (city_1, tile_2), (city_2, tile_3), ...] (-> plus simple pour verifier si les coos d une tile coresspondent à ceux d un des tiles de map.tiles)
        for city_and_tiles in tiles_owned_list:
            city_coo = city_and_tiles[0]
            for tile_coo in city_and_tiles[1]:
                temporary_tiles_owned.append((city_coo, tile_coo))

        map_tiles_coos = {} # pour avoir tous les coos et leurs tiles
        for tile in self.game.map.tiles:
            map_tiles_coos[tuple(tile.coo)] = tile # une key de dict ne peu pas etre un objet immuable et donc pas une liste, c est pour ça que je convertit en tuple

        for city_and_tile in temporary_tiles_owned:
            if tuple(city_and_tile[1]) in map_tiles_coos.keys():
                self.add_tile_owned(map_tiles_coos[tuple(city_and_tile[1])], map_tiles_coos[tuple(city_and_tile[0])])

    def load_units_owned(self, units_owned_list):
        self.units_owned = []

        for unit_data in units_owned_list:
            name = unit_data[0]
            tile_linked_coo = unit_data[1]
            for tile in self.game.map.tiles:
                if tile.coo == tile_linked_coo:
                    unit = self.player_handler.create_unit(name, tile, self.id)
                    unit.current_hp = unit_data[2]
                    unit.current_movement = unit_data[3]
                    self.units_owned.append(unit)
                    
                    unit_type = self.player_handler.find_if_is_unit_or_building(name)
                    if unit_type == "unit":
                        tile.unit = unit
                    elif unit_type == "building":
                        tile.building = unit
                    
                    break
        
        self.update_map_tiles_owner()

    def load_tiles_seen_coos_set(self, list_tiles_seen_coos):
        self.tiles_seen_coos = set()
        for coo in list_tiles_seen_coos:
            self.tiles_seen_coos.add(tuple(coo))

    def get_player_data(self):
        # je dois convertir beaucoup de variables en d autres types sinon bugs avec json 
        # (souvent il y a des bugs quand il y a des int dans des dict ou quand il y a des tuples) (donc les int sont convertis en str, les tuples en list, etc...)
        # (et aussi pour les keys de dicts il faut utiliser des objets immuables)
        return (self.id, self.color, self.get_ressource_storage_to_list(), self.get_tiles_owned(), self.get_units_owned(), list(self.tiles_seen_coos))

    def load_player(self, player_data):
        self.color = player_data[1]
        self.load_ressource_storage_to_dict(player_data[2])
        self.load_tiles_owned(player_data[3])
        self.load_units_owned(player_data[4])
        self.load_tiles_seen_coos_set(player_data[5])
        
        self.update_color_tiles()
        self.get_tiles_seens_with_coos()
        self.calculate_income_and_outcome()

    def create_settler(self):
        possibilities = self.game.map.get_settler_possibilities()
        
        n = randint(0, len(possibilities) - 1)
        #settler = Settler(self.game, possibilities[n], self.id)
        settler = self.player_handler.create_unit("settler", possibilities[n], self.id)
        possibilities[n].unit = settler
        self.units_owned.append(settler)
        self.update_tiles_seen(settler)

    def add_tile_owned(self, tile, city_linked):
        for city_and_tiles in self.tiles_owned:
            if city_and_tiles[0] == city_linked:
                city_and_tiles[1].append(tile) # ajouter la tile 
                
                self.tiles_seen.add(tile) # ajouter la tile dans les tiles_seen
                self.tiles_seen.update(set(self.game.map.return_neighbors_tiles(tile)))
                self.get_tiles_seens_coos_with_tiles()
                
                return # pas besoin de continuer à chercher après avoir trouvé la tile
        
        self.tiles_owned.append((city_linked, [tile]))

    def update_map_tiles_owner(self):
        total_tiles_owned = []
        for city_and_tiles in self.tiles_owned:
            total_tiles_owned += city_and_tiles[1]

        for tile in self.game.map.tiles:
            if tile in total_tiles_owned:
                tile.owner = self.id

    def get_tiles_seens_with_coos(self):
        for tile in self.game.map.tiles:
            if tuple(tile.coo) in self.tiles_seen_coos:
                self.tiles_seen.add(tile)

    def get_tiles_seens_coos_with_tiles(self):
        for tile in self.tiles_seen:
            self.tiles_seen_coos.add(tuple(tile.coo))

    def update_tiles_seen(self, unit): # pour update les tiles_seen seulement autour d une seule unit (ou building) (+ optimisé que de verifier toutes les units)
        neighbors = set(self.game.map.find_possible_neighbors(unit.tile_linked.coo))
        neighbors.add(tuple(unit.tile_linked.coo)) # si la tile n est pas deja dans les tiles_seen (par exemple a la creation du premier settler)
        self.tiles_seen_coos.update(neighbors)
        self.get_tiles_seens_with_coos()

    def update_all_tiles_seen(self):
        for unit in self.units_owned:
            self.update_tiles_seen(unit)

    def move_unit(self, tile):
        if tile != None:
            selected_unit = self.game.map.selected_tile.unit
            if selected_unit != None:
                if selected_unit.owner == self.id:
                    selected_unit.move(tile)
                    selected_unit.update_unit()
                    self.update_tiles_seen(selected_unit)

    def calculate_income_and_outcome(self): # gains + depenses
        self.total_ressource_income = {}

        for ressource_name in RESSOURCES_FILEPATHS.keys():
            self.total_ressource_income[ressource_name] = 0 # pour initialiser tous les revenus à 0

        for city_and_tiles in self.tiles_owned:
            for tile in city_and_tiles[1]:
                for ressource in NORMAL_RESSOURCES[tile.type]:
                    self.total_ressource_income[ressource] += 1

        for unit in self.units_owned:
            for key_1, value_1 in unit.ressource_income.items():
                self.total_ressource_income[key_1] += value_1
            for key_2, value_2 in unit.ressource_outcome.items():
                self.total_ressource_income[key_2] -= value_2

    def calculate_prod_per_city(self):
        for city_and_tiles in self.tiles_owned:
            city_and_tiles[0].building.calculate_regional_prod(city_and_tiles[1])

    def update_ressources(self):
        for key, value in self.total_ressource_income.items():
            self.ressource_storage[key] += value
            
            if self.ressource_storage[key] < 0:
                pass

    def update_color_tiles(self):
        for city_and_tiles in self.tiles_owned:
            #city_and_tiles[0].initial_background_color = self.color
            #city_and_tiles[0].update(False)
            for tile in city_and_tiles[1]:
                tile.initial_background_color = self.color
                tile.update(False)

    def finish_turn(self):
        self.calculate_income_and_outcome()
        self.update_ressources()

        for unit in self.units_owned:
            unit.current_movement = unit.max_movement
        #for healing_unit in self.healing_units: # faire
            #pass
        for city_and_tiles in self.tiles_owned:
            city_and_tiles[0].building.calculate_expansion(city_and_tiles[1])
        self.update_map_tiles_owner() # si jamais j ai oublié de le faire à un moment
        self.get_tiles_seens_coos_with_tiles() # si jamais j ai oublié de faire ça après avoir ajouté des tiles dans tiles_seen (et sans chnager tiles_seen_coos)

class AI_Player(Player):
    def __init__(self, game, id):
        super().__init__(game, id)

    def ai_turn(self):
        #if self.game.map.player_handler.turn == 1: # temporaire
        if self.player_handler.turn == 1:
            self.units_owned[0].special_action() # temporaire

class PlayerHandler:
    def __init__(self, game):
        self.game = game

        self.player_number = 2
        self.players = {} # id = "1" pour main_player, autres numeros pour IAs

        self.turn = 0

    def create_player(self, id):
        if id == "1":
            self.players[id] = Player(self.game, id)
        else:
            self.players[id] = AI_Player(self.game, id)

    def create_unit(self, unit_name, tile_linked, owner):
        if unit_name == "unit":
            return Unit(self.game, tile_linked, owner)
        elif unit_name == "settler":
            return Settler(self.game, tile_linked, owner)
        elif unit_name == "city":
            return City(self.game, tile_linked, owner)
        
    def find_if_is_unit_or_building(self, name):
        units = ["unit", "settler"]
        buildings = ["city"]
        if name in units:
            return "unit"
        elif name in buildings:
            return "building"

    def initial_players(self):
        self.turn = 0
        self.players = {}
        for i in range(self.player_number):
            self.create_player(str(i+1))

        colors = PLAYERS_COLORS.copy()
        for player in self.players.values():
            index = randint(0, len(colors) - 1)
            player.color = colors[index]
            colors.pop(index)

        for player in self.players.values():
            player.create_settler()
            player.calculate_income_and_outcome()
        self.game.ui.page_handler.reload_page()

    def get_players_data(self):
        players_data = [str(self.turn)]
        for player in self.players.values():
            players_data.append(player.get_player_data())
        return players_data
    
    def load_players(self, players_data):
        self.turn = int(players_data[0])
        players_data.pop(0)

        self.players = {}
        for data in players_data:
            self.create_player(data[0])
            self.players[data[0]].load_player(data)
        
        self.game.ui.page_handler.reload_page()

    def next_turn(self):
        if self.game.ui.page_handler.page == 5:
            if self.turn == 0:
                self.game.ui.button_handler.toggle_side_page("HELP_TEXT", False)
            
            self.turn += 1

            for player in self.players.values():
                if player.id != "1":
                    player.ai_turn()
                player.finish_turn()
            self.game.ui.page_handler.reload_page()
