import pygame
import json
import os
import pathlib
from constants import *

class Saves_Handler:
    def __init__(self, game):
        self.game = game
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.current_save = 0

        self.load_settings()

    def make_data_dir(self):
        if not os.path.exists(f"{self.dir_path}/data"):
            os.makedirs(f"{self.dir_path}/data")

    def make_saves_dir(self):
        if not os.path.exists(f"{self.dir_path}/data/saves"):
            os.makedirs(f"{self.dir_path}/data/saves")

    def get_settings(self):
        return {"W":self.game.w, "H":self.game.h, "max_vertical_buttons":self.game.ui.max_vertical_buttons, "max_horizontal_buttons":self.game.ui.max_horizontal_buttons, 
                "menu_bouton_color":self.game.ui.default_background_color, "menu_text_color":self.game.ui.default_text_color, 
                "bouton_zoom":self.game.ui.default_zoom, "arrondissement_bords_boutons":self.game.ui.default_roundness}
    
    def save_settings(self):
        settings = self.get_settings()
        with open (f"{self.dir_path}/data/settings.json", "w") as f:
            json.dump(settings, f)

    def set_settings(self, settings):
        self.game.w = settings["W"]
        self.game.h = settings["H"]
        self.game.screen = pygame.display.set_mode((self.game.w, self.game.h))
        
        self.game.ui.max_vertical_buttons = settings["max_vertical_buttons"]
        self.game.ui.max_horizontal_buttons = round(self.game.ui.max_vertical_buttons * VERTICAL_HORIZONTAL_RATIO)
        self.game.ui.vertical_space = self.game.h // self.game.ui.max_vertical_buttons
        self.game.ui.horizontal_space = self.game.w // self.game.ui.max_horizontal_buttons
        self.game.ui.default_background_color = settings["menu_bouton_color"]
        self.game.ui.default_text_color = settings["menu_text_color"]
        self.game.ui.default_zoom = settings["bouton_zoom"]
        self.game.ui.default_roundness = settings["arrondissement_bords_boutons"]

    def get_saves_numbers(self): # regarde le folder data/saves et renvoie les numeros des files
        saves = []
        path = pathlib.Path(f"{self.dir_path}/data/saves")
        path_str_list_len = len(list(str(path)))
        for child in path.iterdir():
            if pathlib.Path(child).is_file():
                full_name = child
                save_number = list(str(full_name))
                for i in range(path_str_list_len + len("/save_")):
                    save_number.pop(0)
                number = ""
                for i in save_number:
                    if not i.isdigit():
                        break
                    number += i
                saves.append(int(number))
        return saves
    
    def get_current_save(self):
        filepath = f"{self.dir_path}/data/saves/save_{self.current_save}.json"
        with open (filepath, "r") as f:
            save = json.load(f)
        return save

    def write_save(self):
        self.make_saves_dir() # si jamais le folder n existe pas
        save = {"current_tiles":list(self.game.map.tiles_coo)}
        try:
            if self.current_save >= MIN_SAVE and self.current_save <= MAX_SAVE:
                filepath = f"{self.dir_path}/data/saves/save_{self.current_save}.json"
                with open (filepath, "w") as f:
                    json.dump(save, f)
        except Exception:
            print("what ?")

    def clear_saves_dir(self): # supprime files et folders
        self.make_saves_dir() # si jamais le folder n existe pas
        path = pathlib.Path(f"{self.dir_path}/data/saves")
        for child in path.iterdir():
            if pathlib.Path(child).is_file():
                os.remove(child)
            else:
                os.rmdir(child)

    def find_lowest_unused_save(self):
        saves = self.get_saves_numbers()
        possible_saves = []
        for i in range(MIN_SAVE, MAX_SAVE+1):
            if i not in saves:
                possible_saves.append(i)
        if possible_saves == []:
            return MAX_SAVE
        return min(possible_saves)

    def make_data(self):
        self.make_data_dir()
        self.make_saves_dir()

    def load_settings(self):
        try:
            with open(f"{self.dir_path}/data/settings.json", "r") as f:
                settings = json.load(f)
                self.set_settings(settings)
        except Exception:
            self.make_data()
            self.save_settings()
            with open(f"{self.dir_path}/data/settings.json", "r") as f:
                settings = json.load(f)
                self.set_settings(settings)

    def load_save(self):
        save = self.get_current_save()
        self.game.map.load_from_save(save["current_tiles"])
