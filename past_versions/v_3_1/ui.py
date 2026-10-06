import pygame
from constants import *
from random import randint

class Button:
    def __init__(self, ui, name, text, column, line, background_color, text_color, initial_size=1, zoom=BUTTON_ZOOM, roundness=BUTTON_ROUNDNESS, hoverable=True, clickable=True, inputable=False, special_value=None):
        self.ui = ui
        self.game = self.ui.game
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
        self.font = pygame.font.Font(None, round(self.ui.vertical_space * self.current_size))
        self.text_render = self.font.render(self.text, True, self.text_color)
        self.text_size = self.font.size(self.text)

        self.position_background = (round(self.column * self.ui.horizontal_space - (self.text_size[0] * 1.1) / 2), round(self.line * self.ui.vertical_space - (self.text_size[1] * 1.1) / 2))
        self.position_text = (round(self.column * self.ui.horizontal_space - self.text_size[0] / 2), round(self.line * self.ui.vertical_space - self.text_size[1] / 2))
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
    
    def check_collision_with_mouse_clicked(self):
        if self.clickable:
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()
            if mouse_clicked[0] and self.background.collidepoint(mouse_pos):
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
                if self.game.ui.button_handler.current_input_mode:
                    self.input_string = self.game.ui.button_handler.current_input
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
        pygame.draw.rect(self.screen, self.background_color, self.background, border_radius=self.roundness)
        self.screen.blit(self.render, self.position_text)

class ButtonHandler:
    def __init__(self, game, ui:UI):
        self.game = game
        self.ui = ui

        self.current_input_mode = False
        self.current_input = ""

        self.pause = False

    def get_input(self):
        for button in self.ui.button_list:
            if button.saved_input_string != "":
                if button.name == "WIDTH INPUT":
                    try:
                        n = int(button.saved_input_string)
                        if n >= MIN_W and n <= MAX_W:
                            self.game.w = int(button.saved_input_string)
                        elif n < MIN_W:
                            self.game.w = MIN_W
                        elif n > MAX_W:
                            self.game.w = MAX_W 
                        self.game.saves_handler.save_settings()
                        self.ui.full_reload()
                    except ValueError:
                        pass
                    button.saved_input_string = ""
                elif button.name == "HEIGHT INPUT":
                    try:
                        n = int(button.saved_input_string)
                        if n >= MIN_H and n <= MAX_H:
                            self.game.h = int(button.saved_input_string)
                        elif n < MIN_H:
                            self.game.h = MIN_H
                        elif n > MAX_H:
                            self.game.h = MAX_H 
                        self.game.saves_handler.save_settings()
                        self.ui.full_reload()
                    except ValueError:
                        pass
                    button.saved_input_string = ""
                elif button.name == "MAP SIZE":
                    try:
                        n = int(button.saved_input_string)
                        if n >= MIN_LAYERS and n <= MAX_LAYERS:
                            self.game.map.layer_number = int(button.saved_input_string)
                        elif n < MIN_LAYERS:
                            self.game.map.layer_number = MIN_LAYERS
                        elif n > MAX_LAYERS:
                            self.game.map.layer_number = MAX_LAYERS 
                        self.ui.reload_page()
                    except ValueError:
                        pass
                    button.saved_input_string = ""

    def not_input_mode(self):
        for button in self.ui.button_list:
            button.input_mode = False
            #button.reload_background_and_text()
        self.current_input_mode = False
        self.current_input = ""

    def return_input(self):
        for button in self.ui.button_list:
            if button.input_mode:
                button.save_current_input()
        self.not_input_mode()
        self.get_input()

    def back(self):
        self.ui.change_page(self.ui.last_page)
    # presque inutile car ne peut pas etre utilisé 2 fois d affilé, 
    # utile seulement si une page est accessible par plusieurs autre pages car permet de revenir à la page qui nous a amené (c est le cas de la page 4)

    def reset(self):
        self.game.w, self.game.h = W, H
        self.ui.button_variables()
        #self.game.saves_handler.save_settings()
        #self.ui.full_reload()

    def button_color(self):
        colors = ["purple", "blue", "red", "orange", "yellow", "green"]
        for i in range(len(colors)):
            if colors[i] == self.ui.default_background_color:
                self.ui.default_background_color = colors[(i+1)%len(colors)]
                break
        #self.game.saves_handler.save_settings()
        #self.ui.reload_page()

    def text_color(self):
        colors = ["white", "black", "grey"]
        for i in range(len(colors)):
            if colors[i] == self.ui.default_text_color:
                self.ui.default_text_color = colors[(i+1)%len(colors)]
                break
        #self.game.saves_handler.save_settings()
        #self.ui.reload_page()

    def screen_width(self):
        widths = [1280, 1280//1.25, 1280//1.5]
        for i in range(len(widths)):
            if widths[i] == self.game.w:
                self.game.w = widths[(i+1)%len(widths)]
                break
            if i == len(widths) - 1:
                self.game.w = widths[0]
        #self.game.saves_handler.save_settings()
        #self.ui.full_reload()

    def screen_height(self):
        heights = [720, 720//1.25, 720//1.5]
        for i in range(len(heights)):
            if heights[i] == self.game.h:
                self.game.h = heights[(i+1)%len(heights)]
                break
            if i == len(heights) - 1:
                self.game.h = heights[0]
        #self.game.saves_handler.save_settings()
        #self.ui.full_reload()

    def width_input(self, button):
        self.not_input_mode()
        if not button.input_mode:
            button.input_mode = True
            button.input_string = ""
            self.current_input_mode = True

    def height_input(self, button):
        self.not_input_mode()
        if not button.input_mode:
            button.input_mode = True
            button.input_string = ""
            self.current_input_mode = True

    def button_size(self):
        sizes = [8, 10, 12, 14]
        for i in range(len(sizes)):
            if sizes[i] == self.ui.max_vertical_buttons:
                self.ui.max_vertical_buttons = sizes[(i+1)%len(sizes)]
                break
            if i == len(sizes) - 1:
                self.ui.max_vertical_buttons = sizes[0]

    def button_zoom(self):
        zooms = [1.2, 1.3, 1.4, 1.5]
        for i in range(len(zooms)):
            if zooms[i] == self.ui.default_zoom:
                self.ui.default_zoom = zooms[(i+1)%len(zooms)]
                break
            if i == len(zooms) - 1:
                self.ui.default_zoom = zooms[0]

    def map_size(self, button):
        self.not_input_mode()
        if not button.input_mode:
            button.input_mode = True
            button.input_string = ""
            self.current_input_mode = True

    def create_game(self):
        self.game.map.generate_map()
        self.game.saves_handler.write_save()
        self.ui.change_page(5)

    def handle_button(self, button:Button): # remplacer chaque event par une fonction liée au nom du bouton ?
        button_name = button.name
        if self.ui.page == 0: # start menu
            if button_name == "START":
                self.ui.change_page(2)
            elif button_name == "OPTIONS":
                self.ui.change_page(1)
            elif button_name == "EXIT":
                self.game.playing = False
        
        elif self.ui.page == 1: # options menu
            if button_name == "BACK":
                self.ui.change_page(0)
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
                self.width_input(button)
                return # pour eviter le full_reload
            elif button_name == "HEIGHT INPUT":
                self.height_input(button)
                return # pour eviter le full_reload
            elif button_name == "BUTTON SIZE":
                self.button_size()
            elif button_name == "BUTTON ZOOM":
                self.button_zoom()
            self.game.saves_handler.save_settings()
            self.ui.full_reload()
        
        elif self.ui.page == 2: # save menu
            if button_name == "BACK":
                self.ui.change_page(0)
            elif button_name == "NEW GAME":
                self.game.saves_handler.current_save = self.game.saves_handler.find_lowest_unused_save()
                self.ui.change_page(4)
            elif button_name == "LOAD SAVE":
                self.ui.change_page(3)
        
        elif self.ui.page == 3: # saves page
            if button_name == "BACK":
                self.ui.change_page(2)
            elif button_name == "CLEAR SAVES":
                self.game.saves_handler.clear_saves_dir()
                self.ui.full_reload()
            elif button_name == "SAVE NOT USED":
                self.game.saves_handler.current_save = button.special_value
                self.ui.change_page(4)
            elif button_name == "SAVE":
                self.game.saves_handler.current_save = button.special_value
                self.game.saves_handler.load_save()
                self.ui.change_page(5)
        
        elif self.ui.page == 4: # game configuration
            if button_name == "BACK":
                self.back()
            elif button_name == "CREATE GAME":
                self.create_game()
            elif button_name == "MAP SIZE":
                self.map_size(button)
                return
        
        elif self.ui.page == 5: # game page
            if button_name == "QUIT":
                self.ui.change_page(0)
            self.game.saves_handler.write_save()

    def pause_menu(self):
        self.ui.side_buttons_state["PAUSE"] = not self.ui.side_buttons_state["PAUSE"]
        self.ui.side_buttons_state["EXIT"] = not self.ui.side_buttons_state["EXIT"]
        self.ui.side_buttons_state["MAIN MENU"] = not self.ui.side_buttons_state["MAIN MENU"]
        self.ui.side_buttons_state["HELP"] = not self.ui.side_buttons_state["HELP"]
        self.pause = not self.pause
        self.ui.full_reload()

    def handle_side_button(self, button:Button):
        button_name = button.name
        if button_name == "EXIT":
            self.game.playing = False
        elif button_name == "MAIN MENU":
            self.ui.change_page(0)
            self.pause_menu()
        elif button_name == "HELP":
            self.ui.change_page(0)
            self.pause_menu()

class UI:
    def __init__(self, game):
        self.game = game
        self.button_handler = ButtonHandler(self.game, self)

        self.button_variables()
        
        self.page = 0
        self.last_page = self.page
        self.button_list = []
        self.side_button_list = []
        #self.side_buttons_state = {"PAUSE":False, "EXIT": False, "MAIN MENU": False}
        self.get_initial_side_buttons_state()

        self.animated_sea_origin = [self.game.w // 2, self.game.h // 2]
        self.current_sea_time_wait = 0
        self.current_sea_circles = []

        self.reload_page()

    def button_variables(self):
        self.max_vertical_buttons = MAX_VERTICAL_BUTTONS
        self.max_horizontal_buttons = MAX_HORIZONTAL_BUTTONS
        self.vertical_space = self.game.h // self.max_vertical_buttons
        self.horizontal_space = self.game.w // self.max_horizontal_buttons
        self.default_background_color = BUTTON_DEFAULT_BACKGROUND_COLOR
        self.default_text_color = BUTTON_DEFAULT_TEXT_COLOR
        self.default_zoom = BUTTON_ZOOM
        self.default_roundness = BUTTON_ROUNDNESS

    def reload_page(self):
        if not self.button_handler.pause:
            self.button_list = self.get_initial_buttons()
        else:
            self.button_list = []
        self.get_side_buttons()

    def full_reload(self):
        self.game.screen = pygame.display.set_mode((self.game.w, self.game.h))
        self.deactivate_input_mode()
        
        self.vertical_space = self.game.h // self.max_vertical_buttons
        self.horizontal_space = self.game.w // self.max_horizontal_buttons
        self.animated_sea_origin = [self.game.w // 2, self.game.h // 2]
        self.game.saves_handler.load_settings() 
        self.game.map.reset()
        self.reload_page()

    def change_page(self, page):
        self.last_page = self.page
        self.page = page
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
            #pygame.draw.circle(self.game.screen, (0, circle[0] % 256, 255), (self.game.w//2 + self.game.map.tile_horizontal_space//2, self.game.h//2), origin_size * circle[1])
            pygame.draw.circle(self.game.screen, (0, circle[0] % 256, 255), self.animated_sea_origin, origin_size * circle[1])

        if self.button_handler.pause:
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
        diff_factor = 0.5
        #center = self.game.map.coo_to_real_pos_centered(self.game.map.camera_center)
        #diff_with_center = self.game.map.coo_to_real_pos_centered(self.game.map.camera_diff)
        #pos = [center[0] + diff_with_center[0] * diff_factor, center[1] + diff_with_center[1] * diff_factor]
        #self.animated_sea_origin = pos

        self.animated_sea_origin = [
            self.game.w // 2 - self.game.map.coo_to_real_pos(self.game.map.camera_diff)[0] * diff_factor,
            self.game.h // 2 - self.game.map.coo_to_real_pos(self.game.map.camera_diff)[1] * diff_factor
        ]

    def pause_menu_background(self):
        background = pygame.Surface((self.game.w, self.game.h))
        background.set_alpha(120)
        background.fill("grey")
        self.game.screen.blit(background, (0, 0))

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
            if background != None:
                background = pygame.transform.scale(background, (self.game.w, self.game.h)) 
                self.game.screen.blit(background, (0, 0))
            elif (background == None) and (page != 5):
                pygame.draw.rect(self.game.screen, "black", (0, 0, self.game.w, self.game.h))
        except FileNotFoundError:
            #print(f"background for page {self.page} not found")
            pygame.draw.rect(self.game.screen, "black", (0, 0, self.game.w, self.game.h))

        if self.button_handler.pause:
            self.pause_menu_background()

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
            #button_list.append(Button(self, "SAVE", f"SAVE {save}", hoverable=True, clickable=True, column=(self.max_horizontal_buttons/columns_number) * (space + ((save-1)//5) * space), line=(self.max_vertical_buttons/rows_number) + (2 + (save - 1) % 5), background_color="red", is_menu_bouton_color=False, special_value=save))
            button_list.append(Button(self, "SAVE", f"SAVE {save}", self.max_horizontal_buttons/columns_number * (space + ((save-1)//5) * space), self.max_vertical_buttons/rows_number + (2 + (save - 1) % 5), "red", self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness, special_value=save))
            saves_list.remove(save)
        for i in saves_list:
            #button_list.append(Button(self, "SAVE NOT USED", "NOT USED", hoverable=True, clickable=True, column=(self.max_horizontal_buttons/columns_number) * (space + ((i-1)//5) * space), line=(self.max_vertical_buttons/rows_number) + (2 + (i - 1) % 5), background_color="red", is_menu_bouton_color=False, special_value=i))
            button_list.append(Button(self, "SAVE NOT USED", "NOT USED", self.max_horizontal_buttons/columns_number * (space + ((i-1)//5) * space), self.max_vertical_buttons/rows_number + (2 + (i - 1) % 5), "red", self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness, special_value=i))
        return button_list

    def get_initial_buttons(self):
        button_list = []
        if self.page == 0: # start menu
            button_list = [
                        Button(self, "START MENU", "START MENU", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "START", "START", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "OPTIONS", "OPTIONS", self.max_horizontal_buttons//2, self.max_vertical_buttons//2, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "EXIT", "EXIT", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 + 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
        elif self.page == 1: # options menu
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
        elif self.page == 2: # save menu
            button_list = [
                        Button(self, "SAVE MENU", "SAVE MENU", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "NEW GAME", "NEW GAME", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 - 0.5, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "LOAD SAVE", "LOAD SAVE", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 + 0.5, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "BACK", "BACK", self.max_horizontal_buttons//2, self.max_vertical_buttons - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
        elif self.page == 3: # saves page
            button_list = [
                        Button(self, "SAVES", "SAVES", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "CLEAR SAVES", "CLEAR SAVES", self.max_horizontal_buttons//2, self.max_vertical_buttons - 2, "red", self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "BACK", "BACK", self.max_horizontal_buttons//2, self.max_vertical_buttons - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
            button_list += self.saves_buttons()
        elif self.page == 4: # game configuration
            button_list = [
                        Button(self, "GAME CONFIGURATION", "GAME CONFIGURATION", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "MAP SIZE", "MAP SIZE", self.max_horizontal_buttons//2 - 2, self.max_vertical_buttons//2, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness, inputable=True),
                        Button(self, "MAP SIZE INDICATOR", f" {self.game.map.layer_number} ", self.max_horizontal_buttons//2 + 3, self.max_vertical_buttons//2, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "CREATE GAME", "CREATE GAME", self.max_horizontal_buttons//2, self.max_vertical_buttons - 3, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
                        Button(self, "BACK", "BACK", self.max_horizontal_buttons//2, self.max_vertical_buttons - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
        elif self.page == 5: # game page
            button_list = [
                        Button(self, "GAME", "GAME", self.max_horizontal_buttons//2, 1, "blue", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
                        Button(self, "QUIT", "QUIT", self.max_horizontal_buttons//2, self.max_vertical_buttons - 1, self.default_background_color, self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
                        ]
        return button_list
    
    def get_side_buttons(self):
        self.side_buttons = {
            "PAUSE": Button(self, "PAUSE", "PAUSE", self.max_horizontal_buttons//2, 1, "black", self.default_text_color, initial_size=1.2, zoom=self.default_zoom, roundness=self.default_roundness, hoverable=False, clickable=False),
            "EXIT": Button(self, "EXIT", "EXIT", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 - 1, "black", self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
            "MAIN MENU": Button(self, "MAIN MENU", "MAIN MENU", self.max_horizontal_buttons//2, self.max_vertical_buttons//2, "black", self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness),
            "HELP": Button(self, "HELP", "HELP", self.max_horizontal_buttons//2, self.max_vertical_buttons//2 + 1, "black", self.default_text_color, zoom=self.default_zoom, roundness=self.default_roundness)
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
        for key, value in self.side_buttons_state.items():
            if value:
                self.add_side_button(key)
            else:
                self.remove_side_button(key)

    def deactivate_input_mode(self):
        self.button_handler.not_input_mode()
    
    def check_buttons(self):
        for button in self.button_list:
            if button.check_collision_with_mouse_clicked():
                self.button_handler.handle_button(button)
        for side_button in self.side_button_list:
            if side_button.check_collision_with_mouse_clicked():
                self.button_handler.handle_side_button(side_button)

    def show_main_buttons(self):
        for button in self.button_list:
            button.appear()

    def show_side_buttons(self): # a faire
        self.update_side_buttons()
        for side_button in self.side_button_list:
            side_button.appear()

    def show_buttons(self):
        self.show_main_buttons()
        self.show_side_buttons()

    def show_page(self):
        self.load_background()
        self.show_buttons()
