import pygame
import json
import os
import pathlib
import math
from random import randint

global fenetre

#pygame.init()

W, H = 1280, 720
min_W, max_W, min_H, max_H = 1280//2, round(1280*1.2), 720//2, round(720*1.2)
max_vertical_buttons = 10
max_horizontal_buttons = round(max_vertical_buttons * (16 / 9))
menu_bouton_color = "purple" 
menu_text_color = "white" 
bouton_zoom = 1.2
arrondissement_bords_boutons = 10

#fenetre = pygame.display.set_mode((W,H))

game = True
pages_names = ["START MENU", "OPTIONS MENU", "SAVE MENU", "SAVES", "GAME CONFIGUARTION", "GAME"]
current_page = 0
current_page_name = pages_names[0]
current_buttons = []
changing_page = True
current_input_mode = False
current_input = ""
assets_path = "4_pygame/assets"
cursor = "pointer_scifi_b.png"
cursor_filepath = f"{assets_path}/cursors/Default/{cursor}"
tile_number_factor = 1.75
initial_tile_number_factor = tile_number_factor
tiles_columns = round(16 * tile_number_factor)
tile_horizontal_space = W/tiles_columns
tile_space = tile_horizontal_space / math.sqrt(3)
tile_vertical_space = tile_space * (3/2)
tiles_lines = round(H/tile_vertical_space)
current_map = None
current_save = 0
min_save, max_save = 1, 10
current_tiles = [] # car json ne peut pas avoir de set()
current_sea_time_wait = 0
current_sea_circles = []
layer_number = 7

class Button:
    def __init__(self, name, text, hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=max_vertical_buttons//2, 
                 horizontal_space=((W // max_horizontal_buttons)), vertical_space=((H // max_vertical_buttons)), initial_size=1, background_color=menu_bouton_color, text_color=menu_text_color, 
                 roundness=arrondissement_bords_boutons, zoom=bouton_zoom, is_menu_bouton_color=True, is_menu_text_color=True, is_arrondissement_bords_boutons=True,
                 is_bouton_zoom=True, special_value=None):
        self.name = name
        self.text = text
        self.hoverable = hoverable
        self.clickable = clickable
        self.column = column
        self.line = line
        self.horizontal_space = horizontal_space
        self.vertical_space = vertical_space
        self.initial_size = initial_size
        self.current_size = initial_size
        self.background_color = background_color
        self.text_color = text_color
        self.roundness = roundness
        self.zoom = zoom
        self.current_zoom = 1

        self.is_menu_bouton_color = is_menu_bouton_color
        self.is_menu_text_color = is_menu_text_color
        self.is_arrondissement_bords_boutons = is_arrondissement_bords_boutons
        self.is_bouton_zoom = is_bouton_zoom

        self.special_value = special_value # si jamais le bouton doit garder une autre variable

        self.current_size = self.initial_size * self.current_zoom
        self.font = pygame.font.Font(None, round(self.vertical_space * self.current_size))
        self.text_render = self.font.render(self.text, True, self.text_color)
        self.text_size = self.font.size(self.text)

        self.input_mode = False
        self.input_string = ""
        self.input_render = self.font.render(self.input_string, True, "black")
        self.saved_input_string = ""

        self.position_background = (round(self.column * self.horizontal_space - (self.text_size[0] * 1.1) / 2), round(self.line * self.vertical_space - (self.text_size[1] * 1.1) / 2))
        self.position_text = (round(self.column * self.horizontal_space - self.text_size[0] / 2), round(self.line * self.vertical_space - self.text_size[1] / 2))
        self.background = pygame.Rect(self.position_background[0], self.position_background[1], round(self.text_size[0] * 1.1), round(self.text_size[1] * 1.1))

    def update(self):
        global W, H, max_vertical_buttons, max_horizontal_buttons, menu_bouton_color, menu_text_color, arrondissement_bords_boutons, bouton_zoom, current_input_mode, current_input
        if self.is_menu_bouton_color:
            self.background_color = menu_bouton_color
        if self.is_menu_text_color:
            self.text_color = menu_text_color
        if self.is_arrondissement_bords_boutons:
            self.roundness = arrondissement_bords_boutons
        if self.is_bouton_zoom:
            self.zoom = bouton_zoom
        self.horizontal_space = round((W // max_horizontal_buttons))
        self.vertical_space = round((H // max_vertical_buttons))
        self.current_size = self.initial_size * self.current_zoom
        
        if self.input_mode:
            self.input_render = self.font.render(self.input_string, True, "black")
            self.background_color = "white"
            self.text_color = "white"
            if current_input_mode:
                self.input_string = current_input
        else:
            self.save_current_input()
        
        self.font = pygame.font.Font(None, round(self.vertical_space * self.current_size))
        self.text_render = self.font.render(self.text, True, self.text_color)
        self.text_size = self.font.size(self.text)

        self.position_background = (round(self.column * self.horizontal_space - (self.text_size[0] * 1.1) / 2), round(self.line * self.vertical_space - (self.text_size[1] * 1.1) / 2))
        self.position_text = (round(self.column * self.horizontal_space - self.text_size[0] / 2), round(self.line * self.vertical_space - self.text_size[1] / 2))
        self.background = pygame.Rect(self.position_background[0], self.position_background[1], round(self.text_size[0] * 1.1), round(self.text_size[1] * 1.1))

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
    
    def appear(self):
        if self.check_collision_with_mouse_hover():
            self.current_zoom = self.zoom
        else:
            self.current_zoom = 1
        self.update()
        pygame.draw.rect(fenetre, self.background_color, self.background, border_radius=self.roundness)
        fenetre.blit(self.text_render, self.position_text)

        if self.input_mode:
            fenetre.blit(self.input_render, self.position_text)

class Tile:
    def __init__(self, coo, center, inner_radius, outer_radius, color=(0, 225, 0), background_color=(180, 125, 0)):
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

    def draw_background(self):
        self.update()
        pygame.draw.polygon(fenetre, self.background_color, self.background_points)

    def draw_tile(self):
        self.update()
        pygame.draw.polygon(fenetre, self.color, self.points)

class Map:
    def __init__(self):
        global tile_horizontal_space, tile_vertical_space, tiles_columns, tiles_lines, tile_number_factor
        self.horizontal_space = tile_horizontal_space
        self.vertical_space = tile_vertical_space
        self.tile_outer_radius = round((self.horizontal_space / 2)) # = cercle qui passe par milieu des cotés de l haxagone
        self.tile_inner_radius = round(self.vertical_space / 2) # = cercle qui passe par les sommets de l hexagone
        self.tiles_columns = tiles_columns
        self.tiles_lines = tiles_lines
        self.tiles = []
        self.tiles_coo = set()
        self.last_tile_number_factor = tile_number_factor

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
        x = coo[0] * (self.horizontal_space)
        y = coo[1] * (self.vertical_space)
        return (x, y)

    def real_pos_to_coo(self, real_pos):
        x = real_pos[0] / (self.horizontal_space)
        y = real_pos[1] / (self.vertical_space)
        return self.remove_decalage((x, y))
    
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
                hexa = Tile((x, y), self.coo_to_real_pos((x, y)), self.tile_inner_radius, self.tile_outer_radius)
                self.tiles.append(hexa)
                self.tiles_coo.add((x, y))
        print(self.tiles_coo)
    
    def specific_tiles(self, coo_list):
        for coo in coo_list:
            self.tiles.append(Tile(coo, self.coo_to_real_pos(coo), self.tile_inner_radius, self.tile_outer_radius))
            self.tiles_coo.add(coo)

    def layers(self, layers_number):
        coo_list = [set()] # coo_list et une liste de plusieurs sets, chacun correspond à une "layer"
        #coo_list[0].add((self.tiles_columns//2, self.tiles_lines//2))
        coo_list[0].add((tiles_columns//2, tiles_lines//2))
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

    def load_tiles_from_coo(self):
        self.tiles = []
        for coo in self.tiles_coo:
            self.tiles.append(Tile(coo, self.coo_to_real_pos(coo), self.tile_inner_radius, self.tile_outer_radius))

    def generate_map(self, layers_number=5):
        #global current_save
        if layers_number >= 1:
            self.tiles = []
            self.tiles_coo = set()
            self.layers(layers_number)

    def load_from_save(self, coo_list=[]):
        if coo_list != []:
            self.tiles_coo = coo_list
            self.load_tiles_from_coo()

    def update_tile_size(self):
        global W, H, tile_number_factor, tiles_columns, tiles_lines, layer_number
        tiles_columns = round(16 * tile_number_factor)  
        #self.horizontal_space = W/tiles_columns
        #tile_horizontal_space = W/tiles_columns
        #tile_space = self.horizontal_space / math.sqrt(3)
        #self.vertical_space = tile_space * (3/2)
        #tiles_lines = round(H/self.vertical_space)
        tile_horizontal_space = W/tiles_columns
        tile_space = tile_horizontal_space / math.sqrt(3)
        tile_vertical_space = tile_space * (3/2)
        tiles_lines = round(H/tile_vertical_space)
        #self.generate_map(layer_number) # solution temporaire
        #self.load_from_save(self.tiles_coo)
        new_factor = tile_number_factor/self.last_tile_number_factor
        #print(new_factor)
        #print("last :", self.tiles_coo)
        for coo in self.tiles_coo:
            coo = (round(coo[0] * new_factor), round(coo[1] * new_factor))
        #print("new :", self.tiles_coo)
        self.load_from_save(self.tiles_coo)
        self.last_tile_number_factor = tile_number_factor

    def draw_tiles(self):
        for tile in self.tiles:
            tile.draw_background()
        for tile in self.tiles:
            tile.draw_tile()

class Player:
    def __init__(self):
        pass

def make_data_dir():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(f"{dir_path}/data"):
        os.makedirs(f"{dir_path}/data")

def get_settings():
    global W, H, max_vertical_buttons, max_horizontal_buttons, menu_bouton_color, menu_text_color, bouton_zoom, arrondissement_bords_boutons
    settings = {"W":W, "H":H, "max_vertical_buttons":max_vertical_buttons, "max_horizontal_buttons":max_horizontal_buttons, 
                "menu_bouton_color":menu_bouton_color, "menu_text_color":menu_text_color, "bouton_zoom":bouton_zoom, "arrondissement_bords_boutons":arrondissement_bords_boutons}
    return settings

def write_save():
    global current_map, current_save, current_tiles
    if current_map != None:
        current_tiles = list(current_map.tiles_coo)
        save = {"current_tiles":current_tiles}
        try:
            filepath = f"{os.path.dirname(os.path.realpath(__file__))}/data/saves/save_{current_save}.json"
            if current_save >= min_save and current_save <= max_save:
                with open (filepath, "w") as f:
                    json.dump(save, f)
        except Exception:
            print("what ?")

def get_saves_numbers(): # regarde le folder data/saves et renvoie les numeros des files
    saves = []
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = pathlib.Path(f"{dir_path}/data/saves")
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

def get_current_save():
    global current_save
    filepath = f"{os.path.dirname(os.path.realpath(__file__))}/data/saves/save_{current_save}.json"
    with open (filepath, "r") as f:
        save = json.load(f)
    return save

def make_settings_file():
    filepath = f"{os.path.dirname(os.path.realpath(__file__))}/data/settings.json"
    settings = get_settings()
    with open (filepath, "w") as f:
        json.dump(settings, f)

def make_saves_dir():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(f"{dir_path}/data/saves"):
        os.makedirs(f"{dir_path}/data/saves")

def clear_saves_dir(): # supprime files et folders
    global current_save
    current_save = 0
    make_saves_dir() # si jamais le folder n existe pas
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = pathlib.Path(f"{dir_path}/data/saves")
    for child in path.iterdir():
        if pathlib.Path(child).is_file():
            os.remove(child)
        else:
            os.rmdir(child)

def make_data():
    make_data_dir()
    make_settings_file()
    make_saves_dir()

def set_settings(settings):
    global fenetre, W, H, max_vertical_buttons, max_horizontal_buttons, menu_bouton_color, menu_text_color, bouton_zoom, arrondissement_bords_boutons
    W = settings["W"]
    H = settings["H"]
    fenetre = pygame.display.set_mode((W,H))
    max_vertical_buttons = settings["max_vertical_buttons"]
    #max_horizontal_buttons = settings["max_horizontal_buttons"]
    max_horizontal_buttons = round(max_vertical_buttons * (16 / 9))
    menu_bouton_color = settings["menu_bouton_color"]
    menu_text_color = settings["menu_text_color"]
    bouton_zoom = settings["bouton_zoom"]
    arrondissement_bords_boutons = settings["arrondissement_bords_boutons"]

def load_settings():
    global W, H, max_vertical_buttons, max_horizontal_buttons, menu_bouton_color, menu_text_color, bouton_zoom, arrondissement_bords_boutons
    try:
        with open(f"{os.path.dirname(os.path.realpath(__file__))}/data/settings.json", "r") as f:
            settings = json.load(f)
            set_settings(settings)
    except Exception as e:
        make_data()
        with open(f"{os.path.dirname(os.path.realpath(__file__))}/data/settings.json", "r") as f:
            settings = json.load(f)
            set_settings(settings)

def new_map():
    global current_map, layer_number
    current_map = Map()
    current_map.generate_map(layer_number)
    #current_map.generate_map(randint(1, 10))
    write_save()

def load_map():
    global current_map, current_tiles
    current_map = Map()
    current_map.load_from_save(current_tiles)

def load_save():
    global current_save, current_map, current_tiles, min_save, max_save
    if current_save >= min_save and current_save <= max_save:
        try:
            save = get_current_save()
            current_tiles = save["current_tiles"]
            load_map()
            write_save()
        except Exception:
            new_map()

def load_data(): # pour pouvoir rajouter d autres choses plus tard
    load_settings()

def custom_cursor(filepath):
    #pygame.mouse.set_cursor(pygame.mouse.get_pos(), pygame.image.load(filepath))
    try:
        pygame.mouse.set_cursor((0, 0), pygame.image.load(filepath))
    except Exception:
        pass

def reload_tile_size():
    #global tile_number_factor, tiles_columns, tile_horizontal_space, tile_space, tile_vertical_space, tiles_lines, current_map
    #tiles_columns = round(16 * tile_number_factor)  
    #tile_horizontal_space = W/tiles_columns
    #tile_space = tile_horizontal_space / math.sqrt(3)
    #tile_vertical_space = tile_space * (3/2)
    #tiles_lines = round(H/tile_vertical_space)
    #current_map = None

    #global current_map
    #if current_map != None:
        #current_map.update_tile_size()
    
    global current_map
    current_map = None

def reload_page():
    global W, H, max_vertical_buttons, max_horizontal_buttons, menu_bouton_color, menu_text_color, bouton_zoom, arrondissement_bords_boutons, fenetre, current_page, current_buttons, changing_page
    
    max_horizontal_buttons = round(max_vertical_buttons * (16 / 9))

    for button in current_buttons:
        if button.is_menu_bouton_color:
            button.background_color = menu_bouton_color

    for button in current_buttons:
        if button.is_menu_text_color:
            button.text_color = menu_text_color

def full_reload():
    global fenetre, W, H, current_buttons, current_input_mode, current_input
    fenetre = pygame.display.set_mode((W,H))
    current_buttons = []
    current_input_mode = False
    current_input = ""
    reload_tile_size()
    not_input_mode()
    reload_page()
    make_data()
    load_data() 

def set_initial_settings(): # juste un copié collé du début du code pour tout remettre
    global W, H, min_W, max_W, min_H, max_H, max_vertical_buttons, max_horizontal_buttons, menu_bouton_color, menu_text_color, bouton_zoom, arrondissement_bords_boutons
    W, H = 1280, 720
    min_W, max_W, min_H, max_H = 1280//2, round(1280*1.25), H//2, round(720*1.25)
    max_vertical_buttons = 10 
    max_horizontal_buttons = round(max_vertical_buttons * (16 / 9))
    menu_bouton_color = "purple" 
    menu_text_color = "white" 
    bouton_zoom = 1.2 
    arrondissement_bords_boutons = 10

    full_reload()

def saves_buttons():
    global max_horizontal_buttons, max_vertical_buttons, min_save, max_save
    button_list = []
    saves_list = []
    for i in range(min_save, max_save+1):
        saves_list.append(i)
    saves = get_saves_numbers()
    last_max_save = max_save
    while max_save % 5: # si le nombre de sauvgardes n est pas un multiple de 5, on arrondit au prochain multiple de 5 pour l arrangement des sauvgardes 
        max_save += 1  # (il y aura une colonne incomplète, mais mieux qu une colonne qui sort de l ecran)
    columns_number = (3 * (max_save//5))
    rows_number = 12
    space = (columns_number / (max_save//5 + 1))
    max_save = last_max_save # comme on utilise une variable globale, pour eviter de la changer
    for save in saves:
        button_list.append(Button("SAVE", f"SAVE {save}", hoverable=True, clickable=True, column=(max_horizontal_buttons/columns_number) * (space + ((save-1)//5) * space), line=(max_vertical_buttons/rows_number) + (2 + (save - 1) % 5), background_color="red", is_menu_bouton_color=False, special_value=save))
        saves_list.remove(save)
    for i in saves_list:
        button_list.append(Button("SAVE NOT USED", "NOT USED", hoverable=True, clickable=True, column=(max_horizontal_buttons/columns_number) * (space + ((i-1)//5) * space), line=(max_vertical_buttons/rows_number) + (2 + (i - 1) % 5), background_color="red", is_menu_bouton_color=False, special_value=i))
    return button_list

def animated_sea():
    global W, H, current_sea_time_wait, current_sea_circles
    size_constant_factor = 500
    origin_blue_deepness = 150
    origin_size = round((W/5)/tile_number_factor)
    origin_size_factor = 1
    color_change_speed = 0.2
    size_change_speed = color_change_speed * 12
    wait_time = round((origin_blue_deepness / color_change_speed) / 5)

    if current_sea_time_wait == 0:
        current_sea_circles.append([origin_blue_deepness, origin_size_factor])

    pygame.draw.rect(fenetre, (0, 0, 255), (0, 0, W, H))

    for circle in current_sea_circles:
        pygame.draw.circle(fenetre, (0, circle[0] % 256, 255), (W//2 + tile_horizontal_space//2, H//2), origin_size * circle[1])
    
    for circle in range(len(current_sea_circles)):
        if current_sea_circles[circle][0] > 2:
            current_sea_circles[circle][0] -= color_change_speed
            current_sea_circles[circle][1] += size_change_speed / size_constant_factor
        else:
            current_sea_circles.pop(circle)
            break

    current_sea_time_wait = (current_sea_time_wait + 1) % wait_time

def load_background(page):
    global W, H, assets_path, tile_number_factor, tile_horizontal_space
    background = None
    try:
        if page == 0:
            background = pygame.image.load(f"{assets_path}/Nature Landscapes Free Pixel Art/nature_8/origbig.png")
        elif page == 1:
            background = pygame.image.load(f"{assets_path}/Nature Landscapes Free Pixel Art/nature_4/origbig.png")
        elif page == 2:
            background = pygame.image.load(f"{assets_path}/Nature Landscapes Free Pixel Art/nature_6/origbig.png")
        elif page == 3:
            background = pygame.image.load(f"{assets_path}/Nature Landscapes Free Pixel Art/nature_1/origbig.png")
        elif page == 4:
            background = pygame.image.load(f"{assets_path}/Nature Landscapes Free Pixel Art/nature_3/origbig.png")
        elif page == 5:
            animated_sea()
        if background != None:
            background = pygame.transform.scale(background, (W, H)) 
            fenetre.blit(background, (0, 0))
    except FileNotFoundError:
        #print(f"background for {pages_names[page]} not found")
        pass

def get_initial_buttons(page):
    global layer_number
    button_list = []
    if page == 0: # start menu
        button_list = [
                    Button("START MENU", "START MENU", hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=1, initial_size=1.2, background_color="blue", is_menu_bouton_color=False, is_menu_text_color=True, is_arrondissement_bords_boutons=False, is_bouton_zoom=False),
                    Button("START", "START", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//2 - 1),
                    Button("OPTIONS", "OPTIONS", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//2),
                    Button("EXIT", "EXIT", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//2 + 1)
                    ]
    elif page == 1: # options menu
        button_list = [
                    Button("OPTIONS MENU", "OPTIONS MENU", hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=1, initial_size=1.2, background_color="blue", is_menu_bouton_color=False, is_menu_text_color=True, is_arrondissement_bords_boutons=False, is_bouton_zoom=False),
                    Button("RESET", "RESET", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//3, initial_size=0.6),
                    Button("BUTTON COLOR", "BUTTON COLOR", hoverable=True, clickable=True, column=max_horizontal_buttons//3, line=max_vertical_buttons//2 - 1, initial_size=0.6),
                    Button("TEXT COLOR", "TEXT COLOR", hoverable=True, clickable=True, column=max_horizontal_buttons//1.5, line=max_vertical_buttons//2 - 1, initial_size=0.6),
                    Button("SCREEN WIDTH", "SCREEN WIDTH", hoverable=True, clickable=True, column=max_horizontal_buttons//3, line=max_vertical_buttons//2, initial_size=0.6),
                    Button("SCREEN HEIGHT", "SCREEN HEIGHT", hoverable=True, clickable=True, column=max_horizontal_buttons//1.5, line=max_vertical_buttons//2, initial_size=0.6),
                    Button("WIDTH INPUT", "WIDTH INPUT", hoverable=True, clickable=True, column=max_horizontal_buttons//3, line=max_vertical_buttons//2 + 1, initial_size=0.6),
                    Button("HEIGHT INPUT", "HEIGHT INPUT", hoverable=True, clickable=True, column=max_horizontal_buttons//1.5, line=max_vertical_buttons//2 + 1, initial_size=0.6),
                    Button("BUTTON SIZE", "BUTTON SIZE", hoverable=True, clickable=True, column=max_horizontal_buttons//3, line=max_vertical_buttons//2 + 2, initial_size=0.6),
                    Button("BUTTON ZOOM", "BUTTON ZOOM", hoverable=True, clickable=True, column=max_horizontal_buttons//1.5, line=max_vertical_buttons//2 + 2, initial_size=0.6),
                    Button("BACK", "BACK", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons - 1)
                    ]
    elif page == 2: # save menu
        button_list = [
                    Button("SAVE MENU", "SAVE MENU", hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=1, initial_size=1.2, background_color="blue", is_menu_bouton_color=False, is_menu_text_color=True, is_arrondissement_bords_boutons=False, is_bouton_zoom=False),
                    Button("NEW GAME", "NEW GAME", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//2 - 0.5),
                    Button("LOAD SAVE", "LOAD SAVE", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//2 + 0.5),
                    Button("BACK", "BACK", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons - 1)
                    ]
    elif page == 3: # saves page
        button_list = [
                    Button("SAVES", "SAVES", hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=1, initial_size=1.2, background_color="blue", is_menu_bouton_color=False, is_menu_text_color=True, is_arrondissement_bords_boutons=False, is_bouton_zoom=False),
                    Button("BACK", "BACK", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons - 1),
                    Button("CLEAR SAVES", "CLEAR SAVES", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons - 2, background_color="red", is_menu_bouton_color=False)
                    ]
        button_list += saves_buttons()
    elif page == 4: # game configuration
        button_list = [
                    Button("GAME CONFIGUARTION", "GAME CONFIGUARTION", hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=1, initial_size=1.2, background_color="blue", is_menu_bouton_color=False, is_menu_text_color=True, is_arrondissement_bords_boutons=False, is_bouton_zoom=False),
                    Button("MAP SIZE", "MAP SIZE", hoverable=True, clickable=True, column=max_horizontal_buttons//2 - 2, line=max_vertical_buttons//2),
                    Button("MAP SIZE INDICATOR", f" {layer_number} ", hoverable=False, clickable=False, column=max_horizontal_buttons//2 + 3, line=max_vertical_buttons//2),
                    Button("CREATE GAME", "CREATE GAME", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons - 3),
                    Button("BACK", "BACK", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons - 1)
                    ]
    elif page == 5: # game page
        button_list = [
                    Button("GAME", "GAME", hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=1, initial_size=1.2, background_color="blue", is_menu_bouton_color=False, is_menu_text_color=True, is_arrondissement_bords_boutons=False, is_bouton_zoom=False),
                    Button("BACK", "BACK", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons - 1)
                    ]
    return button_list

def find_button(button_name):
    global current_buttons
    for button in current_buttons:
        if button.name == button_name:
            return button

def show_buttons():
    global current_buttons
    for button in current_buttons:
        button.appear()

def show_page():
    global current_page, current_buttons, changing_page
    load_background(current_page)

    if current_buttons == [] or changing_page:
        current_page = current_page
        current_buttons = get_initial_buttons(current_page).copy()

    show_buttons()

def game_page():
    global W, H, current_page, current_buttons, changing_page, assets_path, current_map, tile_horizontal_space, tile_vertical_space, tile_number_factor, initial_tile_number_factor
    page = 5
    load_background(page)

    if current_buttons == [] or current_page != page or changing_page:
        current_page = page
        current_buttons = get_initial_buttons(page)
        tile_number_factor = initial_tile_number_factor
        reload_tile_size()

    if current_map == None:
        load_save()

    current_map.draw_tiles()
    show_buttons()

def not_input_mode():
    global current_input_mode, current_buttons, current_input
    for button in current_buttons:
        button.input_mode = False
    current_input_mode = False
    current_input = ""

def get_inputs():
    global current_buttons, W, H, min_W, max_W, min_H, max_H, layer_number
    for button in current_buttons:
        if button.saved_input_string != "":
            if button.name == "WIDTH INPUT":
                try:
                    n = int(button.saved_input_string)
                    if n >= min_W and n <= max_W:
                        W = int(button.saved_input_string)
                    elif n < min_W:
                        W = min_W
                    elif n > max_W:
                        W = max_W 
                    full_reload()
                except ValueError:
                    #print("not an integer")
                    pass
                button.saved_input_string = ""
            if button.name == "HEIGHT INPUT":
                try:
                    n = int(button.saved_input_string)
                    if n >= min_H and n <= max_H:
                        H = int(button.saved_input_string)
                    elif n < min_H:
                        H = min_H
                    elif n > max_W:
                        H = max_H 
                    full_reload()
                except ValueError:
                    #print("not an integer")
                    pass
                button.saved_input_string = ""
            if button.name == "MAP SIZE":
                try:
                    n = int(button.saved_input_string)
                    if n >= 1 and n <= 15:
                        layer_number = int(button.saved_input_string)
                    elif n < 1:
                        layer_number = 1
                    elif n > 15:
                        layer_number = 15 
                    full_reload()
                except ValueError:
                    #print("not an integer")
                    pass

def button_color():
    global menu_bouton_color
    colors = ["purple", "blue", "red", "orange", "yellow", "green"]
    for i in range(len(colors)):
        if colors[i] == menu_bouton_color:
            menu_bouton_color = colors[(i+1)%len(colors)]
            break

def text_color():
    global menu_text_color
    colors = ["white", "black", "grey"]
    for i in range(len(colors)):
        if colors[i] == menu_text_color:
            menu_text_color = colors[(i+1)%len(colors)]
            break

def screen_width():
    global W
    widths = [1280, 1280//1.25, 1280//1.5]
    for i in range(len(widths)):
        if widths[i] == W:
            W = widths[(i+1)%len(widths)]
            break
        if i == len(widths) - 1:
            W = widths[0]
    full_reload()

def screen_height():
    global H
    heights = [720, 720//1.25, 720//1.5]
    for i in range(len(heights)):
        if heights[i] == H:
            H = heights[(i+1)%len(heights)]
            break
        if i == len(heights) - 1:
            H = heights[0]
    full_reload()

def width_input():
    global current_input_mode
    button = find_button("WIDTH INPUT")
    not_input_mode()
    if not button.input_mode:
        button.input_mode = True
        button.input_string = ""
        current_input_mode = True

def height_input():
    global current_input_mode
    button = find_button("HEIGHT INPUT")
    not_input_mode()
    if not button.input_mode:
        button.input_mode = True
        button.input_string = ""
        current_input_mode = True

def button_size():
    global max_vertical_buttons, max_horizontal_buttons
    sizes = [8, 10, 12, 14]
    for i in range(len(sizes)):
        if sizes[i] == max_vertical_buttons:
            max_vertical_buttons = sizes[(i+1)%len(sizes)]
            break
        if i == len(sizes) - 1:
            max_vertical_buttons = sizes[0]
    full_reload()

def button_zoom():
    global bouton_zoom
    zooms = [1.2, 1.3, 1.4, 1.5]
    for i in range(len(zooms)):
        if zooms[i] == bouton_zoom:
            bouton_zoom = zooms[(i+1)%len(zooms)]
            break
        if i == len(zooms) - 1:
            bouton_zoom = zooms[0]

def map_size():
    global current_input_mode
    button = find_button("MAP SIZE")
    not_input_mode()
    if not button.input_mode:
        button.input_mode = True
        button.input_string = ""
        current_input_mode = True

def find_lowest_unused_save():
    global min_save, max_save
    saves = get_saves_numbers()
    possible_saves = []
    for i in range(min_save, max_save+1):
        if i not in saves:
            possible_saves.append(i)
    if possible_saves == []:
        return max_save
    return min(possible_saves)

def button_handler(button:Button): # remplacer chaque event par une fonction liée au nom du bouton ?
    global W, H, max_vertical_buttons, max_horizontal_buttons, game, current_page, current_buttons, changing_page, bouton_zoom, current_input_mode, current_input, current_save, current_map
    button_name = button.name
    if current_page == 0: # start menu
        if button_name == "START":
            current_page = 2
        elif button_name == "OPTIONS":
            current_page = 1
        elif button_name == "EXIT":
            game = False
    elif current_page == 1: # options menu
        if button_name == "BACK":
            current_page = 0
        elif button_name == "RESET":
            set_initial_settings()
        elif button_name == "BUTTON COLOR":
            button_color()
        elif button_name == "TEXT COLOR":
            text_color()
        elif button_name == "SCREEN WIDTH":
            screen_width()
        elif button_name == "SCREEN HEIGHT":
            screen_height()
        elif button_name == "WIDTH INPUT":
            width_input()
        elif button_name == "HEIGHT INPUT":
            height_input()
        elif button_name == "BUTTON SIZE":
            button_size()
        elif button_name == "BUTTON ZOOM":
            button_zoom()
    elif current_page == 2: # save menu
        if button_name == "BACK":
            current_page = 0
        elif button_name == "LOAD SAVE":
            current_page = 3
        elif button_name == "NEW GAME":
            current_save = find_lowest_unused_save()
            #write_save()
            #load_save()
            #make_data()
            current_page = 4
    elif current_page == 3: # saves page
        if button_name == "BACK":
            current_page = 2
        elif button_name == "SAVE":
            current_save = button.special_value
            write_save()
            load_save()
            make_data()
            current_page = 5
        elif button_name == "SAVE NOT USED":
            current_save = button.special_value
            current_page = 4
        elif button_name == "CLEAR SAVES":
            clear_saves_dir()
            make_data()
            full_reload()
    elif current_page == 4: # game configuration
        if button_name == "BACK":
            current_page = 2
        elif button_name == "MAP SIZE":
            map_size()
        elif button_name == "CREATE GAME":
            new_map()
            current_page = 5
    elif current_page == 5: # game page
        if button_name == "BACK":
            current_page = 2
            current_map = None
    
    reload_page()

def check_events():
    global game, current_buttons, current_input_mode, current_input, tile_number_factor
    for event in pygame.event.get():
        if current_input_mode == True:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    current_input = current_input[:-1]
                elif event.key == pygame.K_RETURN:
                    for button in current_buttons:
                        if button.input_mode:
                            button.save_current_input()
                    current_input_mode = False
                    current_input = ""
                    get_inputs()
                else:
                    current_input += event.unicode
        if event.type == pygame.QUIT:
            game = False
            break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            not_input_mode()
            for button in current_buttons:
                if button.check_collision_with_mouse_clicked():
                    button_handler(button)
        elif event.type == pygame.MOUSEWHEEL:
            min_factor = 0.75
            max_factor = 5
            changing_size_speed = 20 # higher number = slower
            if current_page == 5: # pour ne pas changer la taille de la map si on ne la voit pas (donc si on n est pas sur game_page() )
                amount = event.dict["precise_y"]
                if tile_number_factor + amount / changing_size_speed >= min_factor and tile_number_factor + amount / changing_size_speed <= max_factor:
                    tile_number_factor += amount / changing_size_speed
                elif tile_number_factor + amount / changing_size_speed <= min_factor:
                    tile_number_factor = min_factor
                elif tile_number_factor + amount / changing_size_speed >= max_factor:
                    tile_number_factor = max_factor
                reload_tile_size()

def frame():
    global W, H, fenetre, game, current_page, current_page_name, current_buttons, changing_page, current_input_mode, cursor_filepath, tiles_columns, tiles_lines, current_map, horizontal_space, vertical_space
    current_page_name = pages_names[current_page]
    last_page = current_page
    pygame.display.set_caption(current_page_name)
    pygame.draw.rect(fenetre, 'black', (0, 0, W, H))
    if current_page <= 4:
        show_page()
    elif current_page == 5:
        game_page()
    check_events()
    if last_page != current_page:
        changing_page = True
        current_buttons = []
        not_input_mode()
    else:
        changing_page = False
    pygame.display.update()

def main():
    global fenetre
    pygame.init()
    clock = pygame.time.Clock()
    fenetre = pygame.display.set_mode((W,H))

    load_data()
    custom_cursor(cursor_filepath)
    full_reload()

    while game:
        frame()
        #pygame.time.delay(1000//30)
        delta = clock.tick(30)

    make_data() # if file doesnt exist creates it + saves data

    pygame.quit()

main()

#pygame.quit()

# objectif :
# jeu strategie tour par tour genre civ 6 (grille hexagonale, 4X, arbre technologie, etc...) (en beacoup moins complexe)

# idées d ajouts :
# - menus (exemples : menu de depart, menu options, menus en jeu, mini menus qui ne prennent pas toute la page)
# - sauvegarde
# - mini IA pour les ennemis
# - generation de map

# à faire :
# - faire en sorte que le bouton sur lequel on zoome soit affiché en priorité (donc affiché en dernier pour etre par dessus les autres)
# - pouvoir passer en plein ecran
# - peut etre modifier classe Button pour pouvoir faire disparaitre certains boutons ? (et empecher d interagir avec)
# - peut etre rendre position de certains boutons relative a celle d autres boutons ? car quand on change la taille des boutons, W ou H, ils peuvent s eloigner ou se rapprocher d autres boutons
# - remplacer assets_path par fonction qui recherche son path ? (pour ne pas avoir a le faire manuellement)
# - pour creer systeme grille hexagones : https://www.redblobgames.com/grids/hexagons/
# - ajouter curseurs ? (nouveau type boutons) -> pouvoir deplacer certains objets en restant appuyé dessus (avec souris) ?
# - quand button_size change, boutons décalés ? ou juste non alignés avec titre de la page dès le début et dans ce cas normal ?
# - creer classe ButtonHandler et mettre toutes fonctions liees a button_handler() dedans ? (donc remplacer fonction button_handler() par une classe)
# - comprendre comment obtenir le bon hostpot du cursor (dans custom_cursor())
# - pourquoi y a t il encore espace entre tiles alors qu on ne multiplie plus par 0.85 ? tant que ça marche ça m arrange mais j aimerais comprendre comment ça fonctionne
#   -> c est parce que les hexagones sont tournés : si on retire le "- 30" dans "angle = math.pi / 180 * ((60 * i - 30) % 360)", les hexagones se touchent.
#   -> les hexagones sont séparés par 1 outer_radius et leurs cotés se font face, sauf que leur cotés se situent à 1/2 inner_radius de leur centre, et inner_radius < outer_radius
# - a la place de verifier pour chaque Tile si le souris et dans son outer_radius, verifier la position de la souris et mettre en blanc la Tile qui se trouve sur sa position
# - faire 1 mini menu pour quand on est en jeu et qu'on appuie sur ESCAPE
# - pourquoi pour les sauvegardes dans make_saves_file() (et get_saves() ) la clé est dupliquée ??? normalement sa valeur est changée, pourquoi cela crée une nouvelle clé légèrement différente (avec des '' autour)
#   -> problème réglé en remplaçant les clés par des str (avant c était des int)
# - ajouter une "clock = pygame.time.Clock()" et ajouter un "dt = clock.tick(30) / 1000" pour adapter la vitesse des objets selon delta (dt) 
# -> exemple : pour animated_sea() (car actuellement vitesse de l abimation change selon nombre frames)
# - trouver un meilleur fond pour la mer, et sinon au moins centrer les cercles selon les coordonnées de la Tile au centre de l ile
# - pour système de sauvegardes, faire en sorte de pourvoir charger une map (ne plus utiliser test_3() ), de creer une nouvelle save, d effacer une save, et peut etre de choisir des parametres de depart ?
# - ajouter deplacement camera
# - mettre saves dans differentes files pour eviter lag ?
# - essayer de mieux centrer boutons et de ne pas les deplacer quand button_size change
# - revoir tout le système de sauvgarde, revoir l ordre dans lequel les fonctions sont appelées, créer une fonction qui génère une Map...
# - refaire système de zoom et de dézoom

# à savoir :
# - quand en mode input, DEL pour supprimer des caractères et RETURN pour valider
# - quand on regarde la map, on peut zoomer/dézoomer avec la molette de la souris 
# - numero des sauvgardes a garder entre 1 et 10

# peut etre trop tard maintenant, mais essayer de faire plusieurs files, ne pas tout mettre dans main.py 
# - probleme actuel : comme tout est dans 1 seule file, je fais beacoup de choses manuellement et quand on rajoute des choses il faut changer beacoup de code
# -> probleme de faire plusieurs files (en plus de devoir tout recommencer): variables globales que j update souvent (exemple : celles liees aux settings) : comment les utiliser a travers plusieurs files ? 
# -> les mettre en arguments de chaque fonction ? faire une file à part ? est-ce possible d update une variable d une file A avec une file B (en utilisant "from [file] import *" et "global [variable]") ?
