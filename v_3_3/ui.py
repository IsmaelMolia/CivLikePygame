import pygame
from constants import *
from random import randint

class Button:
    def __init__(self, button_handler, name, text, column, line, background_color, text_color, initial_size=1, zoom=BUTTON_ZOOM, roundness=BUTTON_ROUNDNESS, hoverable=True, clickable=True, inputable=False, special_value=None):
        self.button_handler = button_handler
        self.game = self.button_handler.game
        self.screen = self.game.screen

        self.name = name
        self.text = text

        self.column = column
        self.line = line

        self.initial_background_color = background_color
        self.initial_text_color = text_color
        self.background_color = background_color
        self.text_color = text_color

        self.initial_size = initial_size
        self.current_size = initial_size
        self.zoom = zoom
        self.current_zoom = 1
        self.roundness = roundness

        self.hoverable = hoverable
        self.clickable = clickable
        self.inputable = inputable

        self.special_value = special_value # si jamais le bouton doit garder une autre variable

        self.current_size = self.initial_size * self.current_zoom
        self.last_size = self.current_size
        
        self.reload()

        self.input_mode = False
        self.last_input_mode = False
        self.input_string = ""
        self.input_render = self.font.render(self.input_string, True, "black")
        self.saved_input_string = ""

        self.render = self.text_render

    def reload(self):
        self.font = pygame.font.Font(None, round(self.button_handler.vertical_space * self.current_size))
        self.text_render = self.font.render(self.text, True, self.text_color)
        self.text_size = self.font.size(self.text)

        self.position_background = (round(self.column * self.button_handler.horizontal_space - (self.text_size[0] * 1.1) / 2), round(self.line * self.button_handler.vertical_space - (self.text_size[1] * 1.1) / 2))
        self.position_text = (round(self.column * self.button_handler.horizontal_space - self.text_size[0] / 2), round(self.line * self.button_handler.vertical_space - self.text_size[1] / 2))
        self.background = pygame.Rect(self.position_background[0], self.position_background[1], round(self.text_size[0] * 1.1), round(self.text_size[1] * 1.1))

    def reload_background_and_text(self):
        self.background_color = self.initial_background_color
        self.text_color = self.initial_text_color
        self.reload()

    def check_collision_with_mouse_hover(self):
        if self.hoverable:
            mouse_pos = pygame.mouse.get_pos()
            if self.background.collidepoint(mouse_pos):
                return True
        return False
    
    def check_collision_with_lmb(self):
        if self.clickable:
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()
            if mouse_clicked[0] and self.background.collidepoint(mouse_pos):
                return True
        return False
    
    def check_collision_with_rmb(self):
        if self.clickable:
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()
            if mouse_clicked[2] and self.background.collidepoint(mouse_pos):
                return True
        return False
    
    def save_current_input(self):
        self.saved_input_string = self.input_string
        self.input_string = ""
        self.input_mode = False

    def update(self):
        if self.check_collision_with_mouse_hover():
            self.current_zoom = self.zoom
        else:
            self.current_zoom = 1
        self.current_size = self.initial_size * self.current_zoom
        
        if self.inputable:
            if self.input_mode:
                self.input_render = self.font.render(self.input_string, True, "black")
                self.background_color = "white"
                self.text_color = "black"
                self.reload()
                if self.button_handler.current_input_mode:
                    self.input_string = self.button_handler.current_input
            else:
                self.save_current_input()
        
        if self.last_size != self.current_size:
            self.reload()
        if self.last_input_mode != self.input_mode:
            self.reload_background_and_text()

        if self.input_mode:
            self.render = self.input_render
        else: 
            self.render = self.text_render

        self.last_size = self.current_size
        self.last_input_mode = self.input_mode
    
    def appear(self):
        self.update()
        if self.background_color != None:
            pygame.draw.rect(self.screen, self.background_color, self.background, border_radius=self.roundness)
        self.screen.blit(self.render, self.position_text)

class ButtonHandler:
    def __init__(self, game, ui:UI):
        self.game = game
        self.ui = ui

        self.current_input_mode = False
        self.current_input = ""

        self.button_variables()

        self.button_list = []
        self.side_button_list = []
        self.get_initial_side_buttons_state()

    def button_variables(self):
        self.max_vertical_buttons = MAX_VERTICAL_BUTTONS
        self.max_horizontal_buttons = MAX_HORIZONTAL_BUTTONS
        self.vertical_space = self.game.h // self.max_vertical_buttons
        self.horizontal_space = self.game.w // self.max_horizontal_buttons
        self.default_background_color = BUTTON_DEFAULT_BACKGROUND_COLOR
        self.default_text_color = BUTTON_DEFAULT_TEXT_COLOR
        self.default_zoom = BUTTON_ZOOM
        self.default_roundness = BUTTON_ROUNDNESS

    def change_settings(self, settings):
        self.max_vertical_buttons = settings["max_vertical_buttons"]
        self.max_horizontal_buttons = round(self.max_vertical_buttons * VERTICAL_HORIZONTAL_RATIO)
        self.vertical_space = self.game.h // self.max_vertical_buttons
        self.horizontal_space = self.game.w // self.max_horizontal_buttons
        self.default_background_color = settings["menu_bouton_color"]
        self.default_text_color = settings["menu_text_color"]
        self.default_zoom = settings["bouton_zoom"]
        self.default_roundness = settings["arrondissement_bords_boutons"]

    def saves_buttons(self):
        button_list = []
        saves_list = []
        for i in range(MIN_SAVE, MAX_SAVE+1):
            saves_list.append(i)
        saves = self.game.saves_handler.get_saves_numbers()
        columns_number = (3 * (MAX_SAVE // 5))
        rows_number = 12
        space = (columns_number / (MAX_SAVE//5 + 1))
        for save in saves:
            button_list.append(Button(self, "SAVE", f"SAVE {save}", self.max_horizontal_buttons/columns_number * (space + ((save-1)//5) * space), self.max_vertical_buttons/rows_number + (2 + (save - 1) % 5), "red", self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness, special_value=save))
            saves_list.remove(save)
        for i in saves_list:
            button_list.append(Button(self, "SAVE NOT USED", "NOT USED", self.max_horizontal_buttons/columns_number * (space + ((i-1)//5) * space), self.max_vertical_buttons/rows_number + (2 + (i - 1) % 5), "red", self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness, special_value=i))
        return button_list

    def get_initial_buttons(self):
        button_list = []
        page = self.ui.page_handler.page
        if page == 0: # start menu
            button_list = [
                        Button(self, "START MENU", "START MENU", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "START", "START", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "OPTIONS", "OPTIONS", self.max_horizontal_buttons//2, self.max_vertical_buttons//2, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "EXIT", "EXIT", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 + 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
        elif page == 1: # options menu
            smaller_size = 0.6
            button_list = [
                        Button(self, "OPTIONS MENU", "OPTIONS MENU", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "RESET", "RESET", self.max_horizontal_buttons//2, self.max_vertical_buttons//3, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "BUTTON COLOR", "BUTTON COLOR", self.max_horizontal_buttons//3, self.max_vertical_buttons//2 - 1, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "TEXT COLOR", "TEXT COLOR", self.max_horizontal_buttons//1.5, self.max_vertical_buttons//2 - 1, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "SCREEN WIDTH", "SCREEN WIDTH", self.max_horizontal_buttons//3, self.max_vertical_buttons//2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "SCREEN HEIGHT", "SCREEN HEIGHT", self.max_horizontal_buttons//1.5, self.max_vertical_buttons//2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "WIDTH INPUT", "WIDTH INPUT", self.max_horizontal_buttons//3, self.max_vertical_buttons//2 + 1, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "HEIGHT INPUT", "HEIGHT INPUT", self.max_horizontal_buttons//1.5, self.max_vertical_buttons//2 + 1, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "BUTTON SIZE", "BUTTON SIZE", self.max_horizontal_buttons//3, self.max_vertical_buttons//2 + 2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "BUTTON ZOOM", "BUTTON ZOOM", self.max_horizontal_buttons//1.5, self.max_vertical_buttons//2 + 2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "BACK", "BACK", self.max_horizontal_buttons//2, self.max_vertical_buttons - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
        elif page == 2: # save menu
            button_list = [
                        Button(self, "SAVE MENU", "SAVE MENU", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "NEW GAME", "NEW GAME", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 - 0.5, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "LOAD SAVE", "LOAD SAVE", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 + 0.5, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "BACK", "BACK", self.max_horizontal_buttons//2, self.max_vertical_buttons - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
        elif page == 3: # saves page
            button_list = [
                        Button(self, "SAVES", "SAVES", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "CLEAR SAVES", "CLEAR SAVES", self.max_horizontal_buttons//2, self.max_vertical_buttons - 2, "red", self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "BACK", "BACK", self.max_horizontal_buttons//2, self.max_vertical_buttons - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
            button_list += self.saves_buttons()
        elif page == 4: # game configuration
            smaller_size = 0.6
            smaller_space = 0.75
            tiles_frequences = self.game.map.tiles_frequences
            tiles_frequences_percentages, total_proba = self.game.map.get_tiles_frequences_percentages()
            button_list = [
                        Button(self, "GAME CONFIGURATION", "GAME CONFIGURATION", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "RESET", "RESET", self.max_horizontal_buttons//2, 2, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "MAP SIZE", "MAP SIZE", self.max_horizontal_buttons//2 - 1, self.max_vertical_buttons//2 - smaller_space * 2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "MAP SIZE INDICATOR", f" {self.game.map.layer_number} ", self.max_horizontal_buttons//2 + 2, self.max_vertical_buttons//2 - smaller_space * 2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "PLAIN FREQUENCE", "PLAIN FREQUENCE", self.max_horizontal_buttons//2 - 5.5, self.max_vertical_buttons//2 - smaller_space, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "PLAIN FREQUENCE INDICATOR", f" {tiles_frequences["plain"]} ({tiles_frequences_percentages["plain"]}%) ", self.max_horizontal_buttons//2 - 1.5, self.max_vertical_buttons//2 - smaller_space, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "WATER FREQUENCE", "WATER FREQUENCE", self.max_horizontal_buttons//2 - 5.5, self.max_vertical_buttons//2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "WATER FREQUENCE INDICATOR", f" {tiles_frequences["water"]} ({tiles_frequences_percentages["water"]}%) ", self.max_horizontal_buttons//2 - 1.5, self.max_vertical_buttons//2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "MOUNTAIN FREQUENCE", "MOUNTAIN FREQUENCE", self.max_horizontal_buttons//2 - 5.5, self.max_vertical_buttons//2 + smaller_space, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "MOUNTAIN FREQUENCE INDICATOR", f" {tiles_frequences["mountain"]} ({tiles_frequences_percentages["mountain"]}%) ", self.max_horizontal_buttons//2 - 1.5, self.max_vertical_buttons//2 + smaller_space, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "HILL FREQUENCE", "HILL FREQUENCE", self.max_horizontal_buttons//2 + 3.5, self.max_vertical_buttons//2 - smaller_space, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "HILL FREQUENCE INDICATOR", f" {tiles_frequences["hill"]} ({tiles_frequences_percentages["hill"]}%) ", self.max_horizontal_buttons//2 + 7, self.max_vertical_buttons//2 - smaller_space, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "FOREST FREQUENCE", "FOREST FREQUENCE", self.max_horizontal_buttons//2 + 3, self.max_vertical_buttons//2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "FOREST FREQUENCE INDICATOR", f" {tiles_frequences["forest"]} ({tiles_frequences_percentages["forest"]}%) ", self.max_horizontal_buttons//2 + 7, self.max_vertical_buttons//2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "TOTAL PROBA", "TOTAL PROBA : ", self.max_horizontal_buttons//2 + 3.5, self.max_vertical_buttons//2 + smaller_space, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "TOTAL PROBA INDICATOR", f" {total_proba} (100%)", self.max_horizontal_buttons//2 + 7, self.max_vertical_buttons//2 + smaller_space, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "PLAYER NUMBER", "PLAYER NUMBER : ", self.max_horizontal_buttons//2 - 1, self.max_vertical_buttons//2 + smaller_space * 2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "PLAYER NUMBER INDICATOR", f" {self.game.map.player_handler.player_number} ", self.max_horizontal_buttons//2 + 2, self.max_vertical_buttons//2 + smaller_space * 2, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "FOG OF WAR", "FOG OF WAR : ", self.max_horizontal_buttons//2 - 1, self.max_vertical_buttons//2 + smaller_space * 3, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "FOG OF WAR INDICATOR", f" {self.game.map.fog_of_war} ", self.max_horizontal_buttons//2 + 2, self.max_vertical_buttons//2 + smaller_space * 3, self.default_background_color, self.default_text_color, initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "CREATE GAME", "CREATE GAME", self.max_horizontal_buttons//2, self.max_vertical_buttons - 2, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "BACK", "BACK", self.max_horizontal_buttons//2, self.max_vertical_buttons - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
        elif page == 5: # game page
            button_list = [
                        #Button(self, "GAME", "GAME", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        #Button(self, "QUIT", "QUIT", self.max_horizontal_buttons//2, self.max_vertical_buttons - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
        return button_list
    
    def get_ressource_income_color(self, n):
        if n > 0:
            return "green"
        elif n == 0:
            return "white"
        return "red"
    
    def get_side_buttons(self):
        smallest_size = SMALLEST_SIZE
        smaller_size = SMALLER_SIZE
        slightly_smaller_size = SLIGHTLY_SMALLER_SIZE
        slightly_bigger_size = SLIGHTLY_BIGGER_SIZE
        
        smallest_space = SMALLEST_SPACE
        smaller_space = SMALLER_SPACE
        
        commands_decalage = COMMANDS_DECALAGE
        
        ui_initial_decalage_x = UI_INITIAL_DECALAGE_X
        ui_decalage_x = UI_DECALAGE_X
        ui_decalage_ressources_strat = UI_DECALAGE_RESSOURCES_STRAT
        ui_decalage_income = UI_DECALAGE_INCOME
        ui_decalage_y = UI_DECALAGE_Y
        ui_space = UI_SPACE
        self.ui_space, self.ui_decalage, self.ui_decalage_ressources_strat, self.ui_decalage_income = ui_space, ui_decalage_x, ui_decalage_ressources_strat, ui_decalage_income # utile pour dessiner les icones des ressources ensuite

        self.side_buttons = {
            "PAUSE TEXT 1": Button(self, "PAUSE TEXT 1", "PAUSE", self.max_horizontal_buttons//2, 1, PAUSE_COLOR, self.default_text_color, initial_size=slightly_bigger_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "PAUSE TEXT 2": Button(self, "PAUSE TEXT 2", "HELP", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 - 1, PAUSE_COLOR, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
            "PAUSE TEXT 3": Button(self, "PAUSE TEXT 3", "MAIN MENU", self.max_horizontal_buttons//2, self.max_vertical_buttons//2, PAUSE_COLOR, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
            "PAUSE TEXT 4": Button(self, "PAUSE TEXT 4", "EXIT", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 + 1, PAUSE_COLOR, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
            
            "COMMANDS TEXT 1": Button(self, "COMMANDS TEXT 1", "ESC : pause", 2.5, commands_decalage, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 2": Button(self, "COMMANDS TEXT 2", "IN SAVES :", 2.5, commands_decalage + smaller_space * 2, None, "white", initial_size=slightly_smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 3": Button(self, "COMMANDS TEXT 3", "RMB : del save", 2.5, commands_decalage + smaller_space * 3, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 4": Button(self, "COMMANDS TEXT 4", "IN GAME :", 2.5, commands_decalage + smaller_space * 5, None, "white", initial_size=slightly_smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 5": Button(self, "COMMANDS TEXT 5", "Z, Q, S, D : camera", 2.5, commands_decalage + smaller_space * 6, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 6": Button(self, "COMMANDS TEXT 6", "LMB : select tile", 2.5, commands_decalage + smaller_space * 7, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            #"COMMANDS TEXT 7": Button(self, "COMMANDS TEXT 7", "M : mini-map", 2.5, commands_decalage + smaller_space * 8, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 8": Button(self, "COMMANDS TEXT 8", "SPACE : next turn", 2.5, commands_decalage + smaller_space * 8, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 9": Button(self, "COMMANDS TEXT 9", "C : camera reset", 2.5, commands_decalage + smaller_space * 9, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 10": Button(self, "COMMANDS TEXT 10", "V : view city", 2.5, commands_decalage + smaller_space * 10, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 11": Button(self, "COMMANDS TEXT 11", "B : build menu", 2.5, commands_decalage + smaller_space * 11, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 12": Button(self, "COMMANDS TEXT 12", "E : empires", 2.5, commands_decalage + smaller_space * 12, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 13": Button(self, "COMMANDS TEXT 13", "R : ressources", 2.5, commands_decalage + smaller_space * 13, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 14": Button(self, "COMMANDS TEXT 14", "TILE HOVERED :", self.max_horizontal_buttons - 2.5, smaller_space * 1, None, "white", initial_size=slightly_smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 15": Button(self, "COMMANDS TEXT 15", "1 : unit menu", self.max_horizontal_buttons - 2.5, smaller_space * 2, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 16": Button(self, "COMMANDS TEXT 16", "2 : building menu", self.max_horizontal_buttons - 2.5, smaller_space * 3, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 17": Button(self, "COMMANDS TEXT 17", "3 : move / attack", self.max_horizontal_buttons - 2.5, smaller_space * 4, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 18": Button(self, "COMMANDS TEXT 18", "F : inspect", self.max_horizontal_buttons - 2.5, smaller_space * 5, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 19": Button(self, "COMMANDS TEXT 19", "UNIT :", self.max_horizontal_buttons - 2.5, smaller_space * 7, None, "white", initial_size=slightly_smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 20": Button(self, "COMMANDS TEXT 20", "A : unit special action", self.max_horizontal_buttons - 2.5, smaller_space * 8, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            #"COMMANDS TEXT 21": Button(self, "COMMANDS TEXT 21", "H : heal mode", self.max_horizontal_buttons - 2.5, smaller_space * 9, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            #"COMMANDS TEXT 22": Button(self, "COMMANDS TEXT 22", "K : kill unit", self.max_horizontal_buttons - 2.5, smaller_space * 10, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 23": Button(self, "COMMANDS TEXT 23", "CHEATS :", self.max_horizontal_buttons - 2.5, smaller_space * 10, None, "white", initial_size=slightly_smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "COMMANDS TEXT 24": Button(self, "COMMANDS TEXT 24", "TAB : fog of war", self.max_horizontal_buttons - 2.5, smaller_space * 11, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),

            "UI TEXT 1": Button(self, "UI TEXT 1", f"TURN 0", ui_initial_decalage_x, ui_decalage_y, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 2": Button(self, "UI TEXT 2", f" 0 ", ui_decalage_x + ui_space * 1, ui_decalage_y, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 3": Button(self, "UI TEXT 3", f" 0 ", ui_decalage_x + ui_space * 2, ui_decalage_y, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 4": Button(self, "UI TEXT 4", f" 0 ", ui_decalage_x + ui_space * 3, ui_decalage_y, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 5": Button(self, "UI TEXT 5", f" 0 ", ui_decalage_x + ui_space * 4, ui_decalage_y, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 6": Button(self, "UI TEXT 6", f" 0 ", ui_decalage_x + ui_space * 5 + ui_decalage_ressources_strat, ui_decalage_y, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 7": Button(self, "UI TEXT 7", f" 0 ", ui_decalage_x + ui_space * 6 + ui_decalage_ressources_strat, ui_decalage_y, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 8": Button(self, "UI TEXT 8", f" 0 ", ui_decalage_x + ui_space * 7 + ui_decalage_ressources_strat, ui_decalage_y, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 9": Button(self, "UI TEXT 9", f" +0 ", ui_decalage_x + ui_decalage_income + ui_space * 1, ui_decalage_y, None, self.get_ressource_income_color(0), initial_size=smallest_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 10": Button(self, "UI TEXT 10", f" +0 ", ui_decalage_x + ui_decalage_income + ui_space * 2, ui_decalage_y, None, self.get_ressource_income_color(0), initial_size=smallest_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 11": Button(self, "UI TEXT 11", f" +0 ", ui_decalage_x + ui_decalage_income + ui_space * 3, ui_decalage_y, None, self.get_ressource_income_color(0), initial_size=smallest_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 12": Button(self, "UI TEXT 12", f" +0 ", ui_decalage_x + ui_decalage_income + ui_space * 4, ui_decalage_y, None, self.get_ressource_income_color(0), initial_size=smallest_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 13": Button(self, "UI TEXT 13", f" +0 ", ui_decalage_x + ui_decalage_income + ui_space * 5 + ui_decalage_ressources_strat, ui_decalage_y, None, self.get_ressource_income_color(0), initial_size=smallest_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 14": Button(self, "UI TEXT 14", f" +0 ", ui_decalage_x + ui_decalage_income + ui_space * 6 + ui_decalage_ressources_strat, ui_decalage_y, None, self.get_ressource_income_color(0), initial_size=smallest_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "UI TEXT 15": Button(self, "UI TEXT 15", f" +0 ", ui_decalage_x + ui_decalage_income + ui_space * 7 + ui_decalage_ressources_strat, ui_decalage_y, None, self.get_ressource_income_color(0), initial_size=smallest_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),

            "BUILD TEXT 1": Button(self, "BUILD TEXT 1", f"======= BUILD =======", self.max_horizontal_buttons - 3.2, 0.75 + smaller_space, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "BUILD TEXT 2": Button(self, "BUILD TEXT 2", f"= FOOD ==============", self.max_horizontal_buttons - 3.2, 0.75 + smaller_space * 2.25, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "BUILD TEXT 3": Button(self, "BUILD TEXT 3", f"= WOOD ==============", self.max_horizontal_buttons - 3.2, 0.75 + smaller_space * 4.25, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "BUILD TEXT 4": Button(self, "BUILD TEXT 4", f"= ROCK ==============", self.max_horizontal_buttons - 3.2, 0.75 + smaller_space * 6.25, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "BUILD TEXT 5": Button(self, "BUILD TEXT 5", f"= GOLD ==============", self.max_horizontal_buttons - 3.2, 0.75 + smaller_space * 8.25, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "BUILD TEXT 6": Button(self, "BUILD TEXT 6", f"= OTHER =============", self.max_horizontal_buttons - 3.2, 0.75 + smaller_space * 10.25, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "BUILD TEXT 7": Button(self, "BUILD TEXT 7", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 0, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 0, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 8": Button(self, "BUILD TEXT 8", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 1, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 0, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 9": Button(self, "BUILD TEXT 9", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 2, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 0, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 10": Button(self, "BUILD TEXT 10", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 0, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 1, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 11": Button(self, "BUILD TEXT 11", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 1, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 1, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 12": Button(self, "BUILD TEXT 12", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 2, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 1, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 13": Button(self, "BUILD TEXT 13", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 0, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 2, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 14": Button(self, "BUILD TEXT 14", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 1, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 2, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 15": Button(self, "BUILD TEXT 15", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 2, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 2, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 16": Button(self, "BUILD TEXT 16", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 0, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 3, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 17": Button(self, "BUILD TEXT 17", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 1, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 3, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 18": Button(self, "BUILD TEXT 18", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 2, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 3, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 19": Button(self, "BUILD TEXT 19", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 0, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 4, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 20": Button(self, "BUILD TEXT 20", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 1, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 4, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 21": Button(self, "BUILD TEXT 21", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 2, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 4, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 22": Button(self, "BUILD TEXT 22", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 0, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 4.7, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 23": Button(self, "BUILD TEXT 23", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 1, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 4.7, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),
            "BUILD TEXT 24": Button(self, "BUILD TEXT 24", f"     ", BUILD_ICONS_HORIZONTAL_DECALAGE + BUILD_ICONS_HORIZONTAL_SPACE * 2, BUILD_ICONS_VERTICAL_DECALAGE + BUILD_ICONS_VERTICAL_SPACE * 4.7, "black", "white", initial_size=1, zoom=self.default_zoom, roundness=self.default_roundness),

            "CURRENT_CITY TEXT 1": Button(self, "BUILD TEXT 1", f"======= CITY =======", 3.4, 0.75 + smaller_space, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),

            "TILE TEXT 1": Button(self, "TILE TEXT 1", f"coordinates : None", self.max_horizontal_buttons - 3.25, self.max_vertical_buttons//2 + smaller_space * 2, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "TILE TEXT 2": Button(self, "TILE TEXT 2", f"owner : None", self.max_horizontal_buttons - 3.25, self.max_vertical_buttons//2 + smaller_space * 3, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "TILE TEXT 3": Button(self, "TILE TEXT 3", f"type : None", self.max_horizontal_buttons - 3.25, self.max_vertical_buttons//2 + smaller_space * 4, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "TILE TEXT 4": Button(self, "TILE TEXT 4", f"select unit : ", self.max_horizontal_buttons - 3.5, self.max_vertical_buttons//2 + smaller_space * 5, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "TILE TEXT 5": Button(self, "TILE TEXT 5", "  1  ", self.max_horizontal_buttons - 1, self.max_vertical_buttons//2 + smaller_space * 5, "red", "white", initial_size=slightly_smaller_size, zoom=self.default_zoom, roundness=self.default_roundness),
            "TILE TEXT 6": Button(self, "TILE TEXT 6", f"select building : ", self.max_horizontal_buttons - 3.75, self.max_vertical_buttons//2 + smaller_space * 6, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "TILE TEXT 7": Button(self, "TILE TEXT 7", "  2  ", self.max_horizontal_buttons - 1, self.max_vertical_buttons//2 + smaller_space * 6, "red", "white", initial_size=slightly_smaller_size, zoom=self.default_zoom, roundness=self.default_roundness),
            "TILE TEXT 8": Button(self, "TILE TEXT 8", f"======== TILE ========", self.max_horizontal_buttons - 3.2, self.max_vertical_buttons//2 + smaller_space, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),

            "CURRENT_UNIT TEXT 1": Button(self, "CURRENT_UNIT TEXT 1", f"type : None", 2.7, self.max_vertical_buttons//2 + smaller_space * 2, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "CURRENT_UNIT TEXT 2": Button(self, "CURRENT_UNIT TEXT 2", f"owner : None", 2.7, self.max_vertical_buttons//2 + smaller_space * 3, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "CURRENT_UNIT TEXT 3": Button(self, "CURRENT_UNIT TEXT 3", f"hp : None", 2.7, self.max_vertical_buttons//2 + smaller_space * 4, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "CURRENT_UNIT TEXT 4": Button(self, "CURRENT_UNIT TEXT 4", f"movement : None", 2.7, self.max_vertical_buttons//2 + smaller_space * 5, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "CURRENT_UNIT TEXT 5": Button(self, "CURRENT_UNIT TEXT 5", f"move : ", 2, self.max_vertical_buttons//2 + smaller_space * 6, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "CURRENT_UNIT TEXT 6": Button(self, "CURRENT_UNIT TEXT 6", "  3  ", 3.6, self.max_vertical_buttons//2 + smaller_space * 6, "red", "white", initial_size=slightly_smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "CURRENT_UNIT TEXT 7": Button(self, "CURRENT_UNIT TEXT 7", f"===== UNIT =====", 2.7, self.max_vertical_buttons//2 + smaller_space, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),

            "CURRENT_BUILDING TEXT 1": Button(self, "CURRENT_BUILDING TEXT 1", f"type : None", 2.7, self.max_vertical_buttons//2 + smaller_space * 2, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "CURRENT_BUILDING TEXT 2": Button(self, "CURRENT_BUILDING TEXT 2", f"owner : None", 2.7, self.max_vertical_buttons//2 + smaller_space * 3, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "CURRENT_BUILDING TEXT 3": Button(self, "CURRENT_BUILDING TEXT 3", f"hp : None", 2.7, self.max_vertical_buttons//2 + smaller_space * 4, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "CURRENT_BUILDING TEXT 4": Button(self, "CURRENT_BUILDING TEXT 4", f"=== BUILDING ===", 2.7, self.max_vertical_buttons//2 + smaller_space, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            
            "INSPECT TEXT 1": Button(self, "INSPECT TEXT 1", f" NONE ", self.max_horizontal_buttons//2 - 0.5, self.max_vertical_buttons//2 + smaller_space * 2, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "INSPECT TEXT 2": Button(self, "INSPECT TEXT 2", f" ", self.max_horizontal_buttons//2 - 0.5, self.max_vertical_buttons//2 + smaller_space * 2 + smallest_space * 1, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "INSPECT TEXT 3": Button(self, "INSPECT TEXT 3", f" ", self.max_horizontal_buttons//2 - 0.5, self.max_vertical_buttons//2 + smaller_space * 2 + smallest_space * 2, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "INSPECT TEXT 4": Button(self, "INSPECT TEXT 4", f" ", self.max_horizontal_buttons//2 - 0.5, self.max_vertical_buttons//2 + smaller_space * 2 + smallest_space * 3, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "INSPECT TEXT 5": Button(self, "INSPECT TEXT 5", f" ", self.max_horizontal_buttons//2 - 0.5, self.max_vertical_buttons//2 + smaller_space * 2 + smallest_space * 4, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "INSPECT TEXT 6": Button(self, "INSPECT TEXT 6", f" ", self.max_horizontal_buttons//2 - 0.5, self.max_vertical_buttons//2 + smaller_space * 2 + smallest_space * 5, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "INSPECT TEXT 7": Button(self, "INSPECT TEXT 7", f"====== INSPECT ======", self.max_horizontal_buttons//2 - 0.5, self.max_vertical_buttons//2 + smaller_space, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),

            "HELP_TEXT TEXT 1": Button(self, "HELP_TEXT TEXT 1", "PRESS 'ESC' THEN 'HELP' TO SEE KEYBINDS", self.max_horizontal_buttons//2, ui_decalage_y * 3, None, "white", initial_size=smaller_size, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            }
        
    def get_initial_side_buttons_state(self): # pour pouvoir ajouter des boutons dans "side_buttons" sans avoir a se rappeler de le faire dans "side_buttons_state" :)
        self.side_buttons_state = {}
        self.get_side_buttons()
        for key in self.side_buttons:
            self.side_buttons_state[key] = False

    def add_side_button(self, button_name):
        for side_button in self.side_button_list:
            if side_button.name == button_name:
                return
        self.side_button_list.append(self.side_buttons[button_name])
    
    def remove_side_button(self, button_name):
        for side_button in self.side_button_list:
            if side_button.name == button_name:
                self.side_button_list.remove(side_button)
                return
            
    def update_side_buttons(self):
        #for key, value in self.side_buttons_state.items():
            #if value:
                #self.add_side_button(key)
            #else:
                #self.remove_side_button(key)

        self.side_button_list = []
        for key, value in self.side_buttons_state.items():
            if value:
                self.add_side_button(key)

    def event_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.current_input = self.current_input[:-1]
            elif event.key == pygame.K_RETURN:
                self.return_input()
            else:
                self.current_input += event.unicode

    def check_if_integer(self, text):
        try:
            n = int(text)
            return True
        except ValueError:
            return False

    def get_input(self):
        for button in self.button_list:
            if button.saved_input_string != "":
                if button.name == "WIDTH INPUT":
                    if self.check_if_integer(button.saved_input_string):
                        n = int(button.saved_input_string)
                        if n >= MIN_W and n <= MAX_W:
                            self.game.w = n
                        elif n < MIN_W:
                            self.game.w = MIN_W
                        elif n > MAX_W:
                            self.game.w = MAX_W 
                        self.game.saves_handler.save_settings()
                        self.ui.page_handler.full_reload()
                    button.saved_input_string = ""
                elif button.name == "HEIGHT INPUT":
                    if self.check_if_integer(button.saved_input_string):
                        n = int(button.saved_input_string)
                        if n >= MIN_H and n <= MAX_H:
                            self.game.h = n
                        elif n < MIN_H:
                            self.game.h = MIN_H
                        elif n > MAX_H:
                            self.game.h = MAX_H 
                        self.game.saves_handler.save_settings()
                        self.ui.page_handler.full_reload()
                    button.saved_input_string = ""
                elif button.name == "MAP SIZE":
                    if self.check_if_integer(button.saved_input_string):
                        n = int(button.saved_input_string)
                        if n >= MIN_LAYERS and n <= MAX_LAYERS:
                            self.game.map.layer_number = n
                        elif n < MIN_LAYERS:
                            self.game.map.layer_number = MIN_LAYERS
                        elif n > MAX_LAYERS:
                            self.game.map.layer_number = MAX_LAYERS 
                        self.ui.page_handler.reload_page()
                    button.saved_input_string = ""
                elif button.name == "PLAIN FREQUENCE":
                    if self.check_if_integer(button.saved_input_string):
                        n = int(button.saved_input_string)
                        key_word = "plain"
                        interval = INTERVALS_TILES_PROBABILITIES[key_word]
                        if n >= interval[0] and n <= interval[1]:
                            self.game.map.tiles_frequences[key_word] = n
                        elif n < interval[0]:
                            self.game.map.tiles_frequences[key_word] = interval[0]
                        elif n > interval[1]:
                            self.game.map.tiles_frequences[key_word] = interval[1] 
                        self.ui.page_handler.reload_page()
                elif button.name == "WATER FREQUENCE":
                    if self.check_if_integer(button.saved_input_string):
                        n = int(button.saved_input_string)
                        key_word = "water"
                        interval = INTERVALS_TILES_PROBABILITIES[key_word]
                        if n >= interval[0] and n <= interval[1]:
                            self.game.map.tiles_frequences[key_word] = n
                        elif n < interval[0]:
                            self.game.map.tiles_frequences[key_word] = interval[0]
                        elif n > interval[1]:
                            self.game.map.tiles_frequences[key_word] = interval[1] 
                        self.ui.page_handler.reload_page()
                elif button.name == "MOUNTAIN FREQUENCE":
                    if self.check_if_integer(button.saved_input_string):
                        n = int(button.saved_input_string)
                        key_word = "mountain"
                        interval = INTERVALS_TILES_PROBABILITIES[key_word]
                        if n >= interval[0] and n <= interval[1]:
                            self.game.map.tiles_frequences[key_word] = n
                        elif n < interval[0]:
                            self.game.map.tiles_frequences[key_word] = interval[0]
                        elif n > interval[1]:
                            self.game.map.tiles_frequences[key_word] = interval[1] 
                        self.ui.page_handler.reload_page()
                elif button.name == "FOREST FREQUENCE":
                    if self.check_if_integer(button.saved_input_string):
                        n = int(button.saved_input_string)
                        key_word = "forest"
                        interval = INTERVALS_TILES_PROBABILITIES[key_word]
                        if n >= interval[0] and n <= interval[1]:
                            self.game.map.tiles_frequences[key_word] = n
                        elif n < interval[0]:
                            self.game.map.tiles_frequences[key_word] = interval[0]
                        elif n > interval[1]:
                            self.game.map.tiles_frequences[key_word] = interval[1] 
                        self.ui.page_handler.reload_page()
                elif button.name == "HILL FREQUENCE":
                    if self.check_if_integer(button.saved_input_string):
                        n = int(button.saved_input_string)
                        key_word = "hill"
                        interval = INTERVALS_TILES_PROBABILITIES[key_word]
                        if n >= interval[0] and n <= interval[1]:
                            self.game.map.tiles_frequences[key_word] = n
                        elif n < interval[0]:
                            self.game.map.tiles_frequences[key_word] = interval[0]
                        elif n > interval[1]:
                            self.game.map.tiles_frequences[key_word] = interval[1] 
                        self.ui.page_handler.reload_page()
                elif button.name == "PLAYER NUMBER":
                    if self.check_if_integer(button.saved_input_string):
                        n = int(button.saved_input_string)
                        if n >= MIN_PLAYER_NUMBER and n <= MAX_PLAYER_NUMBER:
                            self.game.map.player_handler.player_number = n
                        elif n < MIN_PLAYER_NUMBER:
                            self.game.map.player_handler.player_number = MIN_PLAYER_NUMBER
                        elif n > MAX_PLAYER_NUMBER:
                            self.game.map.player_handler.player_number = MAX_PLAYER_NUMBER 
                        self.ui.page_handler.reload_page()

    def not_input_mode(self):
        for button in self.button_list:
            button.input_mode = False
            #button.reload_background_and_text()
        self.current_input_mode = False
        self.current_input = ""

    def return_input(self):
        for button in self.button_list:
            if button.input_mode:
                button.save_current_input()
        self.not_input_mode()
        self.get_input()

    def activate_input_button(self, button):
        self.not_input_mode()
        if not button.input_mode:
            button.input_mode = True
            button.input_string = ""
            self.current_input_mode = True

    def back(self):
        self.ui.page_handler.change_page(self.ui.page_handler.last_page)
    # presque inutile car ne peut pas etre utilisé 2 fois d affilé, 
    # utile seulement si une page est accessible par plusieurs autre pages car permet de revenir à la page qui nous a amené (c est le cas de la page 4)

    def reset(self):
        self.game.w, self.game.h = W, H
        self.button_variables()

    def button_color(self):
        colors = ["purple", "blue", "red", "orange", "yellow", "green"]
        for i in range(len(colors)):
            if colors[i] == self.default_background_color:
                self.default_background_color = colors[(i+1)%len(colors)]
                break

    def text_color(self):
        colors = ["white", "black", "grey"]
        for i in range(len(colors)):
            if colors[i] == self.default_text_color:
                self.default_text_color = colors[(i+1)%len(colors)]
                break

    def screen_width(self):
        widths = [1280, 1280//1.25, 1280//1.5]
        for i in range(len(widths)):
            if widths[i] == self.game.w:
                self.game.w = widths[(i+1)%len(widths)]
                break
            if i == len(widths) - 1:
                self.game.w = widths[0]

    def screen_height(self):
        heights = [720, 720//1.25, 720//1.5]
        for i in range(len(heights)):
            if heights[i] == self.game.h:
                self.game.h = heights[(i+1)%len(heights)]
                break
            if i == len(heights) - 1:
                self.game.h = heights[0]

    def button_size(self):
        sizes = [8, 10, 12, 14]
        for i in range(len(sizes)):
            if sizes[i] == self.max_vertical_buttons:
                self.max_vertical_buttons = sizes[(i+1)%len(sizes)]
                break
            if i == len(sizes) - 1:
                self.max_vertical_buttons = sizes[0]

    def button_zoom(self):
        zooms = [1.2, 1.3, 1.4, 1.5]
        for i in range(len(zooms)):
            if zooms[i] == self.default_zoom:
                self.default_zoom = zooms[(i+1)%len(zooms)]
                break
            if i == len(zooms) - 1:
                self.default_zoom = zooms[0]

    def reset_map_settings(self):
        self.game.map.get_tiles_frequences()

    def create_game(self):
        self.game.map.generate_map()
        self.game.saves_handler.write_save()
        self.ui.page_handler.change_page(5)

    def handle_button(self, button:Button): # remplacer chaque event par une fonction liée au nom du bouton ?
        button_name = button.name
        if self.ui.page_handler.page == 0: # start menu
            if button_name == "START":
                self.ui.page_handler.change_page(2)
            elif button_name == "OPTIONS":
                self.ui.page_handler.change_page(1)
            elif button_name == "EXIT":
                self.game.playing = False
        
        elif self.ui.page_handler.page == 1: # options menu
            if button_name == "BACK":
                self.ui.page_handler.change_page(0)
            elif button_name == "RESET":
                self.reset()
            elif button_name == "BUTTON COLOR":
                self.button_color()
            elif button_name == "TEXT COLOR":
                self.text_color()
            elif button_name == "SCREEN WIDTH":
                self.screen_width()
            elif button_name == "SCREEN HEIGHT":
                self.screen_height()
            elif button_name == "WIDTH INPUT":
                self.activate_input_button(button)
                return # pour eviter le full_reload
            elif button_name == "HEIGHT INPUT":
                self.activate_input_button(button)
                return # pour eviter le full_reload
            elif button_name == "BUTTON SIZE":
                self.button_size()
            elif button_name == "BUTTON ZOOM":
                self.button_zoom()
            self.game.saves_handler.save_settings()
            self.ui.page_handler.full_reload()
        
        elif self.ui.page_handler.page == 2: # save menu
            if button_name == "BACK":
                self.ui.page_handler.change_page(0)
            elif button_name == "NEW GAME":
                self.game.saves_handler.current_save = self.game.saves_handler.find_lowest_unused_save()
                self.ui.page_handler.change_page(4)
            elif button_name == "LOAD SAVE":
                self.ui.page_handler.change_page(3)
        
        elif self.ui.page_handler.page == 3: # saves page
            if button_name == "BACK":
                self.ui.page_handler.change_page(2)
            elif button_name == "CLEAR SAVES":
                self.game.saves_handler.clear_saves_dir()
                self.ui.page_handler.full_reload()
            elif button_name == "SAVE NOT USED":
                self.game.saves_handler.current_save = button.special_value
                self.ui.page_handler.change_page(4)
            elif button_name == "SAVE":
                self.game.saves_handler.current_save = button.special_value
                self.game.saves_handler.load_save()
                self.ui.page_handler.change_page(5)
        
        elif self.ui.page_handler.page == 4: # game configuration
            if button_name == "BACK":
                self.back()
            elif button_name == "RESET":
                self.reset_map_settings()
                self.ui.page_handler.reload_page()
            elif button_name == "CREATE GAME":
                self.create_game()
            elif button_name == "MAP SIZE":
                self.activate_input_button(button)
            elif button_name == "PLAIN FREQUENCE":
                self.activate_input_button(button)
            elif button_name == "WATER FREQUENCE":
                self.activate_input_button(button)
            elif button_name == "MOUNTAIN FREQUENCE":
                self.activate_input_button(button)
            elif button_name == "FOREST FREQUENCE":
                self.activate_input_button(button)
            elif button_name == "HILL FREQUENCE":
                self.activate_input_button(button)
            elif button_name == "PLAYER NUMBER":
                self.activate_input_button(button)
            elif button_name == "FOG OF WAR":
                self.game.map.fog_of_war = not self.game.map.fog_of_war
                self.ui.page_handler.reload_page()
        
        elif self.ui.page_handler.page == 5: # game page
            if button_name == "QUIT":
                self.ui.page_handler.change_page(0)
            self.game.saves_handler.write_save()

    def get_side_page_buttons_number(self, side_page_name): # side_page_name doit etre un seul mot, ou sinon avec des "_"
        #n = 0
        #for key in self.side_buttons.keys():
            #text = key.split()
            #try:
                #if (side_page_name in text) and ("TEXT" in text) and (int(text[-1]) >= 0):
                    #n += 1
            #except:
                #pass
        #return n 
        numbers = []
        for key in self.side_buttons.keys():
            text = key.split()
            try:
                if (side_page_name in text) and ("TEXT" in text) and (int(text[-1]) >= 0):
                    numbers.append(text[-1])
            except:
                pass
        return numbers
    
    def update_side_page_buttons_text(self, name, texts):
        n = self.get_side_page_buttons_number(name)
        #for i in range(n):
        for i in range(len(n)):
            try:
                #self.ui.button_handler.side_buttons[f"{name} TEXT {i+1}"].text = texts[i]
                #self.ui.button_handler.side_buttons[f"{name} TEXT {i+1}"].reload()
                self.ui.button_handler.side_buttons[f"{name} TEXT {n[i]}"].text = texts[i]
                self.ui.button_handler.side_buttons[f"{name} TEXT {n[i]}"].reload()
            except: # si jamais len(texts) != n 
                pass

    def update_side_page_buttons_color(self, name, color, buttons_numeros=[], colors=[]):
        if buttons_numeros == []:
            n = self.get_side_page_buttons_number(name)
            for i in range(len(n)):
                self.ui.button_handler.side_buttons[f"{name} TEXT {n[i]}"].initial_text_color = color
                self.ui.button_handler.side_buttons[f"{name} TEXT {n[i]}"].reload_background_and_text()
        elif colors != []:
            for i in range(len(buttons_numeros)):
                self.ui.button_handler.side_buttons[f"{name} TEXT {buttons_numeros[i]}"].initial_text_color = colors[i]
                self.ui.button_handler.side_buttons[f"{name} TEXT {buttons_numeros[i]}"].reload_background_and_text()

    def return_sign_for_str(self, n):
        if n > 0:
            return f"+{n}"
        return f"{n}"
        
    def return_color_for_str(self, n):
        if n > 0:
            return "green"
        elif n == 0:
            return "white"
        return "red"

    def update_text_side_page(self, name):
        if name == "UI":
            current_n = 1
            buttons_numeros = []
            colors = []
            try:
                texts = [f"TURN {self.game.map.player_handler.turn}"]
                for ressource_quantity in self.game.map.player_handler.players["1"].ressource_storage.values():
                    texts.append(f"{ressource_quantity}")
                    current_n += 1
                for ressource_income in self.game.map.player_handler.players["1"].total_ressource_income.values():
                    texts.append(self.return_sign_for_str(ressource_income))
                    current_n += 1
                    buttons_numeros.append(str(current_n))
                    colors.append(self.return_color_for_str(ressource_income))

                self.update_side_page_buttons_text("UI", texts)
                self.update_side_page_buttons_color("UI", "white", buttons_numeros, colors)

            except Exception as e:
                pass # si self.game.map ou self.game.map.player_handler.players["1"] n existent pas encore

        elif name == "BUILD":
            self.ui.page_handler.update_build_icons()

        elif name == "TILE":
            selected_tile = self.game.map.selected_tile
            #tile_coo = f"coordinates : {selected_tile.coo}"
            tile_coo = f"coordinates : {(int(selected_tile.coo[0] - self.game.map.initial_camera_center[0] + 0.5),  -(selected_tile.coo[1] - self.game.map.initial_camera_center[1]))}"
            # pour considerer tile_centrale comme (0, 0) (le + 0.5 est pour ne pas montrer le decalage lié au systeme hexagonal, et il y a un - devant la coordonnée y pour donner l impression qu aller vers le bas siginfie baisser y)
            if (not self.game.map.fog_of_war) or (selected_tile in self.game.map.player_handler.players["1"].tiles_seen):
                tile_owner = f"owner : player {selected_tile.owner}"
                if selected_tile.owner == None:
                    tile_owner = f"owner : None"
                tile_type = f"type : {selected_tile.type}"
            else:
                tile_owner = f"owner : [hidden]"
                tile_type = f"type : [hidden]"
            self.update_side_page_buttons_text("TILE", [tile_coo, tile_owner, tile_type])

            if self.ui.page_handler.state_side_pages["CURRENT_UNIT"]:
                self.update_text_side_page("CURRENT_UNIT")
            elif self.ui.page_handler.state_side_pages["CURRENT_BUILDING"]:
                self.update_text_side_page("CURRENT_BUILDING")
            if self.ui.page_handler.state_side_pages["INSPECT"]:
                self.update_text_side_page("INSPECT")

        elif name == "CURRENT_UNIT":
            try:
                if (not self.game.map.fog_of_war) or (self.game.map.selected_tile in self.game.map.player_handler.players["1"].tiles_seen):
                    selected_tile_unit = self.game.map.selected_tile.unit
                    texts = [f"type : {selected_tile_unit.name}", f"owner : player {selected_tile_unit.owner}", 
                            f"hp : {selected_tile_unit.current_hp}/{selected_tile_unit.max_hp}", f"movement : {selected_tile_unit.current_movement}/{selected_tile_unit.max_movement}"]
                else:
                    texts = [f"type : [hidden]", f"owner : [hidden]", f"hp : [hidden]", f"movement : [hidden]"]
            except: # si selected_tile == None ou selected_tile.unit == None
                texts = [f"type : None", f"owner : None", f"hp : None", f"movement : None"]
            self.update_side_page_buttons_text("CURRENT_UNIT", texts)
            self.side_buttons["CURRENT_UNIT TEXT 6"].background_color = COLOR_BUTTON_ACTIVATED[self.ui.page_handler.moving_unit]
            if self.ui.page_handler.state_side_pages["INSPECT"]:
                self.update_text_side_page("INSPECT")
        
        elif name == "CURRENT_BUILDING":
            try:
                if (not self.game.map.fog_of_war) or (self.game.map.selected_tile in self.game.map.player_handler.players["1"].tiles_seen):
                    selected_tile_building = self.game.map.selected_tile.building
                    texts = [f"type : {selected_tile_building.name}", f"owner : player {selected_tile_building.owner}", 
                            f"hp : {selected_tile_building.current_hp}/{selected_tile_building.max_hp}"]
                else:
                    texts = [f"type : [hidden]", f"owner : [hidden]", f"hp : [hidden]"]
            except: # si selected_tile == None ou selected_tile.building == None
                texts = [f"type : None", f"owner : None", f"hp : None"]
            self.update_side_page_buttons_text("CURRENT_BUILDING", texts)
            if self.ui.page_handler.state_side_pages["INSPECT"]:
                self.update_text_side_page("INSPECT")

        elif name == "INSPECT":
            texts = ["NONE", " ", " ", " ", " ", " "]
            try:
                s_tile = self.game.map.selected_tile
                if (not self.game.map.fog_of_war) or (s_tile in self.game.map.player_handler.players["1"].tiles_seen):
                    if self.ui.page_handler.state_side_pages["CURRENT_UNIT"]:
                        if s_tile.unit != None:
                            texts = INSPECT_DATA[s_tile.unit.name]
                    elif self.ui.page_handler.state_side_pages["CURRENT_BUILDING"]:
                        if s_tile.building != None:
                            texts = INSPECT_DATA[s_tile.building.name]
                            if s_tile.building.name == "city":
                                self.game.map.player_handler.players[s_tile.owner].calculate_prod_per_city() # pour update les regional_prod
                                texts[5] = f"regional prod : {s_tile.building.regional_prod}"
                    else:
                        texts = INSPECT_DATA[s_tile.type]
                        if s_tile.strategic_ressources != []:
                            texts[3] = f"strategic ress : {get_ressources_text(s_tile.strategic_ressources)}"
                else:
                    texts[0] = "[HIDDEN]"
            except: # si selected_tile == None
                #texts = []
                pass
            self.update_side_page_buttons_text("INSPECT", texts)
    
    def toggle_side_page(self, name, bool:bool):
        n = self.get_side_page_buttons_number(name)
        self.ui.page_handler.state_side_pages[name] = bool
        #for i in range(n):
            #self.ui.button_handler.side_buttons_state[f"{name} TEXT {i+1}"] = bool
        for number in n:
            self.ui.button_handler.side_buttons_state[f"{name} TEXT {number}"] = bool

        if name == "PAUSE":
            self.ui.page_handler.pause = bool
            if (not self.ui.page_handler.pause) and (self.ui.page_handler.state_side_pages["COMMANDS"]): # pour etre sur de desactiver cette side_page
                self.toggle_side_page("COMMANDS", not self.ui.page_handler.state_side_pages["COMMANDS"])
            self.ui.page_handler.full_reload()

            if self.ui.page_handler.page == 5 and not bool:
                self.toggle_side_page("UI", True) # pour réactiver l'UI

        elif name == "UI" and bool:
            self.update_text_side_page("UI")

        elif name == "BUILD":
            if bool:
                self.update_text_side_page("BUILD")
                self.toggle_side_page("TILE", False)
                self.toggle_side_page("CURRENT_CITY", False)
                self.game.custom_cursor(CURSORS_FILEPATHS["build"])
            else:
                self.game.custom_cursor(CURSORS_FILEPATHS["default"])

        elif name == "CURRENT_CITY":
            if bool:
                self.toggle_side_page("TILE", False)
                self.toggle_side_page("BUILD", False)
                self.game.custom_cursor(CURSORS_FILEPATHS["city"])
            else:
                self.game.custom_cursor(CURSORS_FILEPATHS["default"])

        elif name == "TILE":
            if bool:
                self.toggle_side_page("BUILD", False)
                self.toggle_side_page("CURRENT_CITY", False)
                self.update_text_side_page("TILE")
            else:
                self.toggle_side_page("CURRENT_BUILDING", False)
                self.toggle_side_page("CURRENT_UNIT", False)
                self.toggle_side_page("INSPECT", False)
        
        elif name == "CURRENT_UNIT":
            self.side_buttons["TILE TEXT 5"].background_color = COLOR_BUTTON_ACTIVATED[self.ui.page_handler.state_side_pages["CURRENT_UNIT"]]
            self.update_text_side_page("CURRENT_UNIT")
            if bool:
                self.toggle_side_page("CURRENT_BUILDING", False) # comme ça unit et building ne peuvent pas être sélectionnés en meme temps
                self.game.custom_cursor(CURSORS_FILEPATHS["unit"]) # important de le faire après self.side_button_select_building(False), sinon le cursor serait remis en "default"
            else:
                self.game.custom_cursor(CURSORS_FILEPATHS["default"])
                self.ui.page_handler.moving_unit = False
        
        elif name == "CURRENT_BUILDING":
            self.side_buttons["TILE TEXT 7"].background_color = COLOR_BUTTON_ACTIVATED[self.ui.page_handler.state_side_pages["CURRENT_BUILDING"]]
            self.update_text_side_page("CURRENT_BUILDING")
            if bool:
                self.toggle_side_page("CURRENT_UNIT", False) # comme ça unit et building ne peuvent pas être sélectionnés en meme temps
                self.game.custom_cursor(CURSORS_FILEPATHS["building"])
            elif not self.ui.page_handler.state_side_pages["CURRENT_UNIT"]:
                self.game.custom_cursor(CURSORS_FILEPATHS["default"])

        elif name == "INSPECT":
            self.update_text_side_page("INSPECT")

    def look_selected_tile(self, selected_tile):
        if selected_tile != None:
            if selected_tile == self.game.map.last_selected_tile:
                self.toggle_side_page("TILE", not self.ui.page_handler.state_side_pages["TILE"]) # si on clique 2 fois sur la meme tile
            elif not self.ui.page_handler.state_side_pages["TILE"]: # pour ne pas avoir à toggle si side page déjà activée
                self.toggle_side_page("TILE", True) # si on clique sur une nouvelle tile
            self.update_text_side_page("TILE")
        elif self.ui.page_handler.state_side_pages["TILE"]:
            self.toggle_side_page("TILE", False) # si on ne clique sur aucune tile
        
        self.game.map.last_selected_tile = selected_tile

    def tile_clicked(self): 
        self.game.map.selected_tile = self.game.map.tile_with_prio        
        self.look_selected_tile(self.game.map.selected_tile)

    def build_menu(self):
        if self.ui.page_handler.page == 5:
            self.toggle_side_page("BUILD", not self.ui.page_handler.state_side_pages["BUILD"])

    def view_city(self):
        if self.ui.page_handler.page == 5:
            if self.game.map.tile_with_prio != None:
                self.toggle_side_page("CURRENT_CITY", not self.ui.page_handler.state_side_pages["CURRENT_CITY"])
            else:
                pass

    def select_current_unit(self):
        if self.ui.page_handler.page == 5:
            if self.game.map.tile_with_prio != None:
                self.game.map.selected_tile = self.game.map.tile_with_prio
                bool = True
                if self.game.map.last_selected_tile == self.game.map.selected_tile:
                    bool = not self.ui.page_handler.state_side_pages["CURRENT_UNIT"]
                if bool:
                    if not self.ui.page_handler.state_side_pages["TILE"]:
                        self.toggle_side_page("TILE", True)
                    else:
                        self.update_text_side_page("TILE")
                elif DEACTIVATE_INSPECT_IF_NOT_UNIT_AND_BUILDING and (not self.ui.page_handler.state_side_pages["CURRENT_BUILDING"]) and (self.ui.page_handler.state_side_pages["INSPECT"]):
                    # pour etre sur de desactiver le inspect (si UNIT et BUILDING sont à False)
                    self.toggle_side_page("INSPECT", False)
                self.toggle_side_page("CURRENT_UNIT", bool) # important de faire après le toggle TILE, car remet le curseur à default
                self.game.map.last_selected_tile = self.game.map.selected_tile
            else:
                self.toggle_side_page("TILE", False)

    def select_current_building(self):
        if self.ui.page_handler.page == 5:
            if self.game.map.tile_with_prio != None:
                self.game.map.selected_tile = self.game.map.tile_with_prio
                bool = True
                if self.game.map.last_selected_tile == self.game.map.selected_tile:
                    bool = not self.ui.page_handler.state_side_pages["CURRENT_BUILDING"]
                if bool:
                    if not self.ui.page_handler.state_side_pages["TILE"]:
                        self.toggle_side_page("TILE", True)
                    else:
                        self.update_text_side_page("TILE")
                elif DEACTIVATE_INSPECT_IF_NOT_UNIT_AND_BUILDING and (not self.ui.page_handler.state_side_pages["CURRENT_UNIT"]) and (self.ui.page_handler.state_side_pages["INSPECT"]):
                    # pour etre sur de desactiver le inspect (si UNIT et BUILDING sont à False)
                    self.toggle_side_page("INSPECT", False)
                self.toggle_side_page("CURRENT_BUILDING", bool)
                self.game.map.last_selected_tile = self.game.map.selected_tile
            else:
                self.toggle_side_page("TILE", False)

    def moving_unit_mode(self):
        #if self.ui.page_handler.state_side_pages["CURRENT_UNIT"]:
            #self.ui.page_handler.moving_unit = not self.ui.page_handler.moving_unit
        #else:
            #self.select_current_unit()
            #self.ui.page_handler.moving_unit = True

        if self.ui.page_handler.page == 5:
            if self.game.map.tile_with_prio != None:
                self.game.map.selected_tile = self.game.map.tile_with_prio
                bool = True
                if self.game.map.last_selected_tile == self.game.map.selected_tile:
                    bool = not self.ui.page_handler.moving_unit
                else:
                    self.update_text_side_page("TILE")
                if bool:
                    if not self.ui.page_handler.state_side_pages["CURRENT_UNIT"]:
                        if not self.ui.page_handler.state_side_pages["TILE"]:
                            self.toggle_side_page("TILE", True)
                        self.toggle_side_page("CURRENT_UNIT", True)
                    self.game.custom_cursor(CURSORS_FILEPATHS["moving"])
                elif self.ui.page_handler.state_side_pages["CURRENT_UNIT"]:
                    self.game.custom_cursor(CURSORS_FILEPATHS["unit"])
                self.ui.page_handler.moving_unit = bool
                self.game.map.last_selected_tile = self.game.map.selected_tile
                #self.side_buttons["CURRENT_UNIT TEXT 6"].background_color = COLOR_BUTTON_ACTIVATED[self.ui.page_handler.moving_unit]
                self.update_text_side_page("CURRENT_UNIT")
            else:
                self.toggle_side_page("TILE", False)

    def inspect_menu(self):
        if self.ui.page_handler.page == 5:
            if self.game.map.tile_with_prio != None:
                self.game.map.selected_tile = self.game.map.tile_with_prio
                bool = True
                if self.game.map.last_selected_tile == self.game.map.selected_tile:
                    bool = not self.ui.page_handler.state_side_pages["INSPECT"]
                else:
                    self.update_text_side_page("TILE")
                if bool:
                    #if (not self.ui.page_handler.state_side_pages["CURRENT_UNIT"]) and (not self.ui.page_handler.state_side_pages["CURRENT_BUILDING"]):
                        if not self.ui.page_handler.state_side_pages["TILE"]:
                            self.toggle_side_page("TILE", True)
                        #self.toggle_side_page("CURRENT_UNIT", True) # donc si UNIT et BUIDLING sont à False, UNIT sera activé
                    #self.game.custom_cursor(CURSORS_FILEPATHS["moving"])
                #elif self.ui.page_handler.state_side_pages["CURRENT_UNIT"]:
                    #self.game.custom_cursor(CURSORS_FILEPATHS["unit"])
                self.toggle_side_page("INSPECT", bool)
                self.game.map.last_selected_tile = self.game.map.selected_tile
            else:
                self.toggle_side_page("TILE", False)

    def handle_side_button(self, button:Button):
        button_name = button.name
        if button_name == "PAUSE TEXT 2":
            self.toggle_side_page("COMMANDS", not self.ui.page_handler.state_side_pages["COMMANDS"])
        elif button_name == "PAUSE TEXT 3":
            self.toggle_side_page("PAUSE", not self.ui.page_handler.pause)
            if self.ui.page_handler.page == 5:
                self.game.saves_handler.write_save()
            self.ui.page_handler.change_page(0)
        elif button_name == "PAUSE TEXT 4":
            self.game.playing = False

        if self.ui.page_handler.page == 5:
            if button_name == "TILE TEXT 5":
                self.toggle_side_page("CURRENT_UNIT", not self.ui.page_handler.state_side_pages["CURRENT_UNIT"])
            elif button_name == "TILE TEXT 7":
                self.toggle_side_page("CURRENT_BUILDING", not self.ui.page_handler.state_side_pages["CURRENT_BUILDING"])

    def check_buttons(self):
        mouse_state = pygame.mouse.get_pressed()
        button_clicked = False
        if mouse_state[0]:
            for button in self.button_list:
                if button.check_collision_with_lmb():
                    self.handle_button(button)
                    button_clicked = True
            for side_button in self.side_button_list:
                if side_button.check_collision_with_lmb():
                    self.handle_side_button(side_button)
                    button_clicked = True

            if (self.ui.page_handler.page == 5) and (not button_clicked): # pour ne pas déselectionner une tile si on clique sur un bouton
                if self.ui.page_handler.moving_unit:
                    self.game.map.player_handler.players["1"].move_unit(self.game.map.tile_with_prio)
                else:
                    self.tile_clicked()
        if mouse_state[2]:
            if self.ui.page_handler.page == 3:
                for button in self.button_list:
                    if button.name == "SAVE" and button.check_collision_with_rmb():
                        self.game.saves_handler.del_save(button.special_value)
                        self.ui.page_handler.full_reload()
            elif self.ui.page_handler.page == 5:
                #if self.ui.page_handler.state_side_pages["CURRENT_UNIT"]:
                    #self.game.map.player_handler.players["1"].move_unit(self.game.map.tile_with_prio)
                #else:
                    #self.select_current_unit()
                pass

    def show_main_buttons(self):
        for button in self.button_list:
            button.appear()

    def show_side_buttons(self):
        self.update_side_buttons()
        for side_button in self.side_button_list:
            side_button.appear()

    def show_buttons(self):
        self.show_main_buttons()
        self.show_side_buttons()

class PageHanlder:
    def __init__(self, game, ui:UI):
        self.game = game
        self.ui = ui

        self.page = 0
        self.last_page = self.page
        self.get_initial_side_pages_state()

        self.pause = False
        self.moving_unit = False

        self.animated_sea_origin = [self.game.w // 2, self.game.h // 2]
        self.current_sea_time_wait = 0
        self.current_sea_circles = []

    def reload_page(self):
        if not self.pause:
            self.ui.button_handler.button_list = self.ui.button_handler.get_initial_buttons()
        else:
            self.ui.button_handler.button_list = []
        self.ui.button_handler.get_side_buttons()
        self.get_side_pages()
        self.update_ui_icons()
        self.update_build_icons()

        self.ui.button_handler.toggle_side_page("TILE", False)
        self.ui.button_handler.toggle_side_page("BUILD", False)
        self.ui.button_handler.toggle_side_page("CITY", False)

    def full_reload(self):
        self.game.screen = pygame.display.set_mode((self.game.w, self.game.h))
        self.ui.button_handler.not_input_mode()
        
        self.ui.button_handler.vertical_space = self.game.h // self.ui.button_handler.max_vertical_buttons
        self.ui.button_handler.horizontal_space = self.game.w // self.ui.button_handler.max_horizontal_buttons
        self.animated_sea_origin = [self.game.w // 2, self.game.h // 2]
        self.game.saves_handler.load_settings() 
        self.game.map.reset()
        self.reload_page()

    def animated_sea(self):
        origin_blue_deepness = 150
        origin_size_factor = 1
        origin_size = round((self.game.w/5)/self.game.map.tile_number_factor)
        size_constant_factor = 500
        color_change_speed = 0.2
        size_change_speed = color_change_speed * 12
        wait_time = round((origin_blue_deepness / color_change_speed) / 5)

        pygame.draw.rect(self.game.screen, (0, 0, 255), (0, 0, self.game.w, self.game.h))

        for circle in self.current_sea_circles:
            pygame.draw.circle(self.game.screen, (0, circle[0] % 256, 255), self.animated_sea_origin, origin_size * circle[1])

        if self.pause:
            return
        
        for circle in range(len(self.current_sea_circles)):
            if self.current_sea_circles[circle][0] > 2:
                self.current_sea_circles[circle][0] -= color_change_speed
                self.current_sea_circles[circle][1] += size_change_speed / size_constant_factor
            else:
                self.current_sea_circles.pop(circle)
                break

        if self.current_sea_time_wait == 0:
            self.current_sea_circles.append([origin_blue_deepness, origin_size_factor])

        self.current_sea_time_wait = (self.current_sea_time_wait + 1) % wait_time

    def update_center_animated_sea(self):
        diff_factor = 0.75
        self.animated_sea_origin = [
            self.game.w // 2 - self.game.map.coo_to_real_pos(self.game.map.camera_diff)[0] * diff_factor,
            self.game.h // 2 - self.game.map.coo_to_real_pos(self.game.map.camera_diff)[1] * diff_factor
        ]
    
    def pause_menu_background(self):
        background = pygame.Surface((self.game.w, self.game.h))
        background.set_alpha(120)
        background.fill("grey")
        
        self.game.screen.blit(background, (0, 0))

    def update_ui_icons(self):
        self.ressources_icons = {}
        self.ressources_icons_positions = {}
        
        self.icon_space = self.ui.button_handler.ui_space * self.ui.button_handler.horizontal_space
        self.icon_decalage = self.ui.button_handler.ui_decalage * self.ui.button_handler.horizontal_space
        #self.icon_decalage_income = self.ui.button_handler.ui_decalage_income # comme ça l espace entre l icone, la quantité de ressource et l income est le même
        self.icon_decalage_income = ICON_DECALAGE_INCOME
        self.icon_strat_decalage = self.ui.button_handler.ui_decalage_ressources_strat * self.ui.button_handler.horizontal_space
        self.icon_size = self.ui.button_handler.vertical_space * ICON_SIZE
        
        i = 1
        for key, value in RESSOURCES_FILEPATHS.items():
            #self.ressources_icons[key] = pygame.image.load(value)
            self.ressources_icons[key] = pygame.transform.scale(pygame.image.load(value), (self.icon_size, self.icon_size)) 

            if i < 5:
                self.ressources_icons_positions[key] = (self.icon_decalage + self.icon_space * (i - self.icon_decalage_income), self.game.h // 100)
            else:
                self.ressources_icons_positions[key] = (self.icon_decalage + self.icon_strat_decalage + self.icon_space * (i - self.icon_decalage_income), self.game.h // 100) # pour ajouter un espace entre ressources normales et ressources stratégiques
            
            i += 1

    def update_build_icons(self):
        self.buildings_icons = {}
        self.buildings_icons_positions = {}

        self.building_icons_size = self.ui.button_handler.vertical_space * BUILD_ICON_SIZE
        
        self.build_horizontal_space = self.ui.button_handler.horizontal_space * BUILD_ICONS_HORIZONTAL_SPACE
        self.build_vertical_space = self.ui.button_handler.vertical_space * BUILD_ICONS_VERTICAL_SPACE
        
        self.build_horizontal_decalage = self.ui.button_handler.horizontal_space * BUILD_ICONS_HORIZONTAL_DECALAGE
        self.build_vertical_decalage = self.ui.button_handler.vertical_space * BUILD_ICONS_VERTICAL_DECALAGE

        for key, value in BUILDINGS_FILEPATHS.items():
            self.buildings_icons[key] = pygame.transform.scale(pygame.image.load(value), (self.building_icons_size, self.building_icons_size)) 
            self.buildings_icons_positions[key] = (self.build_horizontal_decalage + self.build_horizontal_space * BUILD_ICONS_POSITIONS[key][0] - self.building_icons_size // 2, self.build_vertical_decalage + self.build_vertical_space * BUILD_ICONS_POSITIONS[key][1] - self.building_icons_size // 2)

    def ui_icons(self):
        for key, value in self.ressources_icons.items():
            self.game.screen.blit(value, self.ressources_icons_positions[key])

    def build_icons(self):
        for key, value in self.buildings_icons.items():
            self.game.screen.blit(value, self.buildings_icons_positions[key])

    def load_background(self):
        background = None
        page = self.page
        try:
            if page == 0:
                background = pygame.image.load(f"{ASSETS_PATH}/Nature Landscapes Free Pixel Art/nature_8/origbig.png")
            elif page == 1:
                background = pygame.image.load(f"{ASSETS_PATH}/Nature Landscapes Free Pixel Art/nature_4/origbig.png")
            elif page == 2:
                background = pygame.image.load(f"{ASSETS_PATH}/Nature Landscapes Free Pixel Art/nature_6/origbig.png")
            elif page == 3:
                background = pygame.image.load(f"{ASSETS_PATH}/Nature Landscapes Free Pixel Art/nature_1/origbig.png")
            elif page == 4:
                background = pygame.image.load(f"{ASSETS_PATH}/Nature Landscapes Free Pixel Art/nature_3/origbig.png")
            elif page == 5:
                self.animated_sea()
                #pygame.draw.rect(self.game.screen, (0, 0, 255), (0, 0, self.game.w, self.game.h))
            if background != None:
                background = pygame.transform.scale(background, (self.game.w, self.game.h)) 
                self.game.screen.blit(background, (0, 0))
            elif (background == None) and (page != 5):
                pygame.draw.rect(self.game.screen, "black", (0, 0, self.game.w, self.game.h))
        except FileNotFoundError:
            pygame.draw.rect(self.game.screen, "black", (0, 0, self.game.w, self.game.h))

        if self.pause:
            self.pause_menu_background()

    def change_page(self, page):
        self.last_page = self.page
        self.page = page
        
        if page == 5:
            self.ui.button_handler.toggle_side_page("UI", True)
            if self.game.map.player_handler.turn == 0:
                self.ui.button_handler.toggle_side_page("HELP_TEXT", True)
        else:
            self.ui.button_handler.toggle_side_page("UI", False)
            self.ui.button_handler.toggle_side_page("HELP_TEXT", False)
        
        self.reload_page()

    def get_initial_side_pages_state(self):
        self.state_side_pages = {
            "COMMANDS":False,
            "UI":False,
            "BUILD":False,
            "MINIMAP":False,
            "TILE":False,
            "CURRENT_UNIT":False,
            "CURRENT_BUILDING":False,
            "CURRENT_CITY":False,
            "INSPECT":False,
            "HELP_TEXT":False
        }

    def get_side_pages(self):
        self.side_pages_rects = {
            "COMMANDS":[pygame.rect.Rect(round((self.game.w // 3) * -0.1), 0, self.game.w // 3, self.game.h), pygame.rect.Rect(round((self.game.w // 3) * 2.1), 0, self.game.w // 3, self.game.h)],
            "UI":[pygame.rect.Rect(round(self.game.w * -0.1), 0, round(self.game.w * 1.2), round(self.ui.button_handler.vertical_space * 0.7))],
            "BUILD":[pygame.rect.Rect(round((self.game.w // 3) * 1.95), round((self.game.h // 2) * 0.2), self.game.w // 3, round((self.game.h // 2) * 1.75))],
            "MINIMAP":[],
            "TILE":[pygame.rect.Rect(round((self.game.w // 3) * 1.95), round((self.game.h // 2) * 1.05), self.game.w // 3, round((self.game.h // 2) * 0.9))],
            "CURRENT_UNIT":[pygame.rect.Rect(round((self.game.w // 4) * 0.1), round((self.game.h // 2) * 1.05), self.game.w // 4, round((self.game.h // 2) * 0.9))],
            "CURRENT_BUILDING":[pygame.rect.Rect(round((self.game.w // 4) * 0.1), round((self.game.h // 2) * 1.05), self.game.w // 4, round((self.game.h // 2) * 0.9))],
            "CURRENT_CITY":[pygame.rect.Rect(round((self.game.w // 4) * 0.1), round((self.game.h // 2) * 0.2), self.game.w // 3, round((self.game.h // 2) * 1.75))],
            "INSPECT":[pygame.rect.Rect(round((self.game.w // 4) * 1.175), round((self.game.h // 2) * 1.05), self.game.w // 3, round((self.game.h // 2) * 0.9))],
            "HELP_TEXT":[]
        }

        for side_page in self.side_pages_rects.keys():
            try:
                self.ui.button_handler.update_text_side_page(side_page)
            except:
                pass

    def check_side_pages(self): # pas très optimisé :/
        #if self.ui.page_handler.page != 5:
        if ((self.page != self.last_page) and (self.last_page == 5)) or (self.pause):
            self.ui.button_handler.toggle_side_page("UI", False)
            self.ui.button_handler.toggle_side_page("BUILD", False)
            self.ui.button_handler.toggle_side_page("MINIMAP", False)
            self.ui.button_handler.toggle_side_page("TILE", False)
            self.ui.button_handler.toggle_side_page("CURRENT_UNIT", False)
            self.ui.button_handler.toggle_side_page("CURRENT_BUILDING", False)
            self.ui.button_handler.toggle_side_page("CURRENT_CITY", False)
            self.ui.button_handler.toggle_side_page("INSPECT", False)
            self.ui.button_handler.toggle_side_page("HELP_TEXT", False)

    def show_side_pages(self):
        self.check_side_pages()
        for key, value in self.state_side_pages.items():
            if value:
                if key != "PAUSE":
                    for rect in self.side_pages_rects[key]:
                        pygame.draw.rect(self.game.screen, SIDE_PAGES_COLORS[key], rect, border_radius=UI_ROUNDNESS)

    def show_icons(self):
        for key, value in self.state_side_pages.items():
            if value:
                if key != "PAUSE":
                    if key == "UI":
                        self.ui_icons()
                    if key == "BUILD":
                        self.build_icons()

    def show_map(self):
        if self.page == 5:
            self.game.map.update_camera()
            self.game.map.draw_tiles()

    def show_page(self):
        self.load_background()
        self.show_map()
        self.show_side_pages()

class UI:
    def __init__(self, game):
        self.game = game
        self.button_handler = ButtonHandler(self.game, self)
        self.page_handler = PageHanlder(self.game, self)
        self.page_handler.reload_page()

    def show(self):
        self.page_handler.show_page()
        self.button_handler.show_buttons()
        self.page_handler.show_icons()
