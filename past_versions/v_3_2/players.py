from random import randint
import pygame
from units import *
from constants import *

class Player:
    def __init__(self, game, id):
        self.game = game
        self.id = id
        self.color = TILE_BACKGROUND_COLOR
        
        self.tiles_owned = []
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

    def load_ressource_storage_to_dict(self, ressource_list):
        self.ressource_storage = {}
        for ressource in ressource_list:
            self.ressource_storage[ressource[0]] = ressource[1]

    def load_tiles_seen_coos_set(self, list_tiles_seen_coos):
        self.tiles_seen_coos = set()
        for coo in list_tiles_seen_coos:
            self.tiles_seen_coos.add(tuple(coo))

    def load_player(self):
        for tile in self.game.map.tiles:
            if tile.owner == self.id:
                self.tiles_owned.append(tile)
                if tile.building != None:
                    self.units_owned.append(tile.building)
            if tile.unit != None:
                if tile.unit.owner == self.id:
                    self.units_owned.append(tile.unit)
        self.update_color_tiles()
        self.get_tiles_seens_with_coos()
        self.calculate_income_and_outcome()

    def create_settler(self):
        possibilities = self.game.map.get_settler_possibilities()
        
        n = randint(0, len(possibilities) - 1)
        settler = Settler(self.game, possibilities[n], self.id)
        possibilities[n].unit = settler
        self.units_owned.append(settler)
        self.update_tiles_seen(settler)

    def get_tiles_seens_with_coos(self):
        for tile in self.game.map.tiles:
            if tuple(tile.coo) in self.tiles_seen_coos:
                self.tiles_seen.add(tile)

    def update_tiles_seen(self, unit): # pour update les tiles_seen seulement autour d une seule unit (ou building) (+ optimisé que de verifier toutes les units)
        #if self.game.map.fog_of_war: # car inutile de modifier tiles_seen si il n y a pas fog_of_war # en fait peut etre qu utile si on passe de sans fog_of_war à avec fog_of_war ? sinon aucune tile visible
            neighbors = set(self.game.map.find_possible_neighbors(unit.tile_linked.coo))
            neighbors.add(unit.tile_linked.coo) # si la tile n est pas deja dans les tiles_seen (par exemple a la creation du premier settler)
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

        for tile in self.tiles_owned:
            for ressource in NORMAL_RESSOURCES[tile.type]:
                self.total_ressource_income[ressource] += 1

        for unit in self.units_owned:
            for key_1, value_1 in unit.ressource_income.items():
                self.total_ressource_income[key_1] += value_1
            for key_2, value_2 in unit.ressource_outcome.items():
                self.total_ressource_income[key_2] -= value_2

    def update_ressources(self):
        for key, value in self.total_ressource_income.items():
            self.ressource_storage[key] += value
            
            if self.ressource_storage[key] < 0:
                pass

    def update_color_tiles(self):
        for tile in self.tiles_owned:
            tile.initial_background_color = self.color
            tile.update(False)

    def finish_turn(self):
        self.calculate_income_and_outcome()
        self.update_ressources()

        for unit in self.units_owned:
            unit.current_movement = unit.max_movement
        #for healing_unit in self.healing_units: # faire
            #pass

class AI_Player(Player):
    def __init__(self, game, id):
        super().__init__(game, id)

    def ai_turn(self):
        if self.game.map.player_handler.turn == 1: # temporaire
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

    def get_players_ids(self):
        # je dois convertir beaucoup de variables en d autres types sinon bugs avec json
        players_ids = [str(self.turn)]
        for player in self.players.values():
            #id = (player.id, player.color, player.tiles_owned, player.units_owned, player.ressource_storage, player.tiles_seen_coos)
            id = (player.id, player.color, player.get_ressource_storage_to_list(), list(player.tiles_seen_coos)) # pas besoin de "player.tiles_owned" ni de "player.units_owned" car ces infos sont dans les tiles
            players_ids.append(id)
        return players_ids
    
    def load_players(self, players_ids):
        self.turn = int(players_ids[0])
        players_ids.pop(0)

        self.players = {}
        for id in players_ids:
            self.create_player(id[0]) 
            self.players[id[0]].color = id[1]
            self.players[id[0]].load_ressource_storage_to_dict(id[2])
            self.players[id[0]].load_tiles_seen_coos_set(id[3])
            self.players[id[0]].load_player()
        self.game.ui.page_handler.reload_page()

    def next_turn(self):
        if self.game.ui.page_handler.page == 5:
            self.turn += 1

            for player in self.players.values():
                player.finish_turn()
                if player.id != "1":
                    player.ai_turn()
            self.game.ui.page_handler.reload_page()
