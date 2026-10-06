import pygame
import json
import os

pygame.init() # important pour les Font

# variables au choix début

W, H = 1280, 720
min_W, max_W, min_H, max_H = 1280//2, round(1280*1.2), 720//2, round(720*1.2)
max_vertical_buttons = 10 # je recommande 10 (en dessous problèmes de décalage et au dessus boutons trop petits)
max_horizontal_buttons = round(max_vertical_buttons * (16 / 9))
#max_horizontal_buttons = round(max_vertical_buttons * (W / H))
menu_bouton_color = "purple" # environ (175, 0, 255) ?
menu_text_color = "white" # (255, 255, 255)
bouton_zoom = 1.2 # je recommande 1.2 (facteur de zoom quand on passe sa souris sur un bouton) 
                  # (eviter de mettre en dessous de 1 sinon bugs de collision car la souris n est plus dessus quand rétrécit, donc se rétércit et s aggrandit en boucle)
arrondissement_bords_boutons = 10 # je recoomande 10 ou 15 (-1 ou moins pour ne pas en avoir)

# variables au choix fin

fenetre = pygame.display.set_mode((W,H))

game = True
pages_names = ["START MENU", "OPTIONS MENU", "GAME"]
current_page = 0
current_page_name = pages_names[0]
current_buttons = []
changing_page = True
current_input_mode = False
current_input = ""
assets_path = "4_pygame/assets" # remplacer par fonction qui recherche fichier assets

class Button:
    def __init__(self, name, text, hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=max_vertical_buttons//2, 
                 horizontal_space=round((W // max_horizontal_buttons)), vertical_space=((H // max_vertical_buttons)), initial_size=1, background_color=menu_bouton_color, text_color=menu_text_color, 
                 roundness=arrondissement_bords_boutons, zoom=bouton_zoom, is_menu_bouton_color=True, is_menu_text_color=True, is_arrondissement_bords_boutons=True,
                 is_bouton_zoom=True):
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
        global H, max_vertical_buttons, menu_bouton_color, menu_text_color, arrondissement_bords_boutons, bouton_zoom, current_input_mode, current_input
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

    def check_collision_with_mouse_hover(self): # si la souris survole le bouton
        if self.hoverable:
            mouse_pos = pygame.mouse.get_pos()
            if self.background.collidepoint(mouse_pos):
                return True
        return False
    
    def check_collision_with_mouse_clicked(self): # si clique gauche sur le bouton
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
    def __init__(self):
        pass

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

def make_settings_file():
    filepath = f"{os.path.dirname(os.path.realpath(__file__))}/data/settings.json"
    settings = get_settings()
    with open (filepath, "w") as f:
        json.dump(settings, f)

def make_data():
    make_data_dir()
    make_settings_file()

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

def load_data():
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

def reload_page():
    global W, H, max_vertical_buttons, max_horizontal_buttons, menu_bouton_color, menu_text_color, bouton_zoom, arrondissement_bords_boutons, fenetre, current_page, current_buttons, changing_page
    
    for button in current_buttons:
        if button.is_menu_bouton_color:
            button.background_color = menu_bouton_color

    for button in current_buttons:
        if button.is_menu_text_color:
            button.text_color = menu_text_color

def full_reload():
    global fenetre, W, H, current_buttons, current_input_mode, current_input
    fenetre = pygame.display.set_mode((W,H)) # fait clignoter ecran en noir
    current_buttons = []
    current_input_mode = False
    current_input = ""
    reload_page()
    make_data()
    load_data() # fait clignoter ecran en noir

def almost_full_reload(): # essayer de faire pareil que full_reload() sans faire clignoter ecran en noir (si c est possible)
    pass

def menu(button_list:list):
    global current_buttons
    for button in button_list:
        button.appear()
    current_buttons = button_list

def set_initial_settings(): # juste un copié collé du début du code pour tout remettre
    global W, H, min_W, max_W, min_H, max_H, max_vertical_buttons, max_horizontal_buttons, menu_bouton_color, menu_text_color, bouton_zoom, arrondissement_bords_boutons
    W, H = 1280, 720
    min_W, max_W, min_H, max_H = 1280//2, round(1280*1.25), H//2, round(720*1.25)
    max_vertical_buttons = 10 # je recommande 10 (en dessous problèmes de décalage et au dessus boutons trop petits)
    max_horizontal_buttons = round(max_vertical_buttons * (16 / 9))
    menu_bouton_color = "purple" # environ (175, 0, 255) ?
    menu_text_color = "white" # (255, 255, 255)
    bouton_zoom = 1.2 # je recommande 1.2 (facteur de zoom quand on passe sa souris sur un bouton) 
                    # (eviter de mettre en dessous de 1 sinon bugs de collision car la souris n est plus dessus quand rétrécit, donc se rétércit et s aggrandit en boucle)
    arrondissement_bords_boutons = 10 # je recoomande 10 ou 15 (-1 ou moins pour ne pas en avoir)

    full_reload()

def get_initial_buttons(page):
    button_list = []
    if page == 0: # start menu
        button_list = [Button("START MENU", "START MENU", hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=1, initial_size=1.2, background_color="blue", is_menu_bouton_color=False, is_menu_text_color=True, is_arrondissement_bords_boutons=False, is_bouton_zoom=False),
                    Button("START", "START", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//2.5),
                    Button("OPTIONS", "OPTIONS", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//2),
                    Button("EXIT", "EXIT", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//1.5)]
    elif page == 1: # options menu
        button_list = [Button("OPTIONS MENU", "OPTIONS MENU", hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=1, initial_size=1.2, background_color="blue", is_menu_bouton_color=False, is_menu_text_color=True, is_arrondissement_bords_boutons=False, is_bouton_zoom=False),
                   Button("RESET", "RESET", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//3, initial_size=0.6),
                   Button("BUTTON COLOR", "BUTTON COLOR", hoverable=True, clickable=True, column=max_horizontal_buttons//3, line=max_vertical_buttons//2 - 1, initial_size=0.6),
                   Button("TEXT COLOR", "TEXT COLOR", hoverable=True, clickable=True, column=max_horizontal_buttons//1.5, line=max_vertical_buttons//2 - 1, initial_size=0.6),
                   Button("SCREEN WIDTH", "SCREEN WIDTH", hoverable=True, clickable=True, column=max_horizontal_buttons//3, line=max_vertical_buttons//2, initial_size=0.6),
                   Button("SCREEN HEIGHT", "SCREEN HEIGHT", hoverable=True, clickable=True, column=max_horizontal_buttons//1.5, line=max_vertical_buttons//2, initial_size=0.6),
                   Button("WIDTH INPUT", "WIDTH INPUT", hoverable=True, clickable=True, column=max_horizontal_buttons//3, line=max_vertical_buttons//2 + 1, initial_size=0.6),
                   Button("HEIGHT INPUT", "HEIGHT INPUT", hoverable=True, clickable=True, column=max_horizontal_buttons//1.5, line=max_vertical_buttons//2 + 1, initial_size=0.6),
                   Button("BUTTON SIZE", "BUTTON SIZE", hoverable=True, clickable=True, column=max_horizontal_buttons//3, line=max_vertical_buttons//2 + 2, initial_size=0.6),
                   Button("BUTTON ZOOM", "BUTTON ZOOM", hoverable=True, clickable=True, column=max_horizontal_buttons//1.5, line=max_vertical_buttons//2 + 2, initial_size=0.6),
                   Button("BACK", "BACK", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons - 1)]
    elif page == 2: # game page
        button_list = [Button("GAME", "GAME", hoverable=False, clickable=False, column=max_horizontal_buttons//2, line=1, initial_size=1.2, background_color="blue", is_menu_bouton_color=False, is_menu_text_color=True, is_arrondissement_bords_boutons=False, is_bouton_zoom=False),
                   Button("BACK", "BACK", hoverable=True, clickable=True, column=max_horizontal_buttons//2, line=max_vertical_buttons//2)]
    return button_list

def find_button(button_name):
    global current_buttons
    for button in current_buttons:
        if button.name == button_name:
            return button

def start_menu():
    global current_page, current_buttons, changing_page, assets_path
    page = 0
    try:
        background_0 = pygame.image.load(f"{assets_path}/Nature Landscapes Free Pixel Art/nature_8/origbig.png")
        background_0 = pygame.transform.scale(background_0, (W, H)) 
        fenetre.blit(background_0, (0, 0))
    except FileNotFoundError as e:
        print(f"background for {pages_names[page]} not found")

    if current_buttons == [] or current_page != page or changing_page:
        current_page = page
        current_buttons = get_initial_buttons(page).copy()

    menu(current_buttons)

def options_menu():
    global current_page, current_buttons, changing_page, assets_path
    page = 1
    try:
        background_0 = pygame.image.load(f"{assets_path}/Nature Landscapes Free Pixel Art/nature_4/origbig.png")
        background_0 = pygame.transform.scale(background_0, (W, H)) 
        fenetre.blit(background_0, (0, 0))
    except FileNotFoundError as e:
        print(f"background for {pages_names[page]} not found")

    if current_buttons == [] or current_page != page or changing_page:
        current_page = page
        current_buttons = get_initial_buttons(page)

    menu(current_buttons)

def game_page():
    global current_page, current_buttons, changing_page, assets_path
    page = 2
    try:
        background_0 = pygame.image.load(f"{assets_path}/Nature Landscapes Free Pixel Art/nature_3/origbig.png")
        background_0 = pygame.transform.scale(background_0, (W, H)) 
        fenetre.blit(background_0, (0, 0))
    except FileNotFoundError as e:
        print(f"background for {pages_names[page]} not found")

    if current_buttons == [] or current_page != page or changing_page:
        current_page = page
        current_buttons = get_initial_buttons(page)

    menu(current_buttons)

def not_input_mode():
    global current_input_mode, current_buttons, current_input
    for button in current_buttons:
        button.input_mode = False
    current_input_mode = False
    current_input = ""

def get_inputs():
    global current_buttons, W, H, min_W, max_W, min_H, max_H
    for button in current_buttons:
        if button.saved_input_string != "":
            if button.name == "WIDTH INPUT":
                try:
                    n = int(button.saved_input_string)
                    if n >= min_W and n <= max_W:
                        W = int(button.saved_input_string)
                    elif n < min_W:
                        W = min_W
                    elif n > min_W:
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
                    elif n > min_H:
                        H = max_H 
                    full_reload()
                except ValueError:
                    #print("not an integer")
                    pass
                button.saved_input_string = ""

def button_handler(button_name): # remplacer chaque event par une fonction liée au nom du bouton ?
    global W, H, max_vertical_buttons, max_horizontal_buttons, game, current_page, menu_bouton_color, menu_text_color, current_buttons, changing_page, bouton_zoom, current_input_mode, current_input
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
            colors = ["purple", "blue", "red", "orange", "yellow", "green"]
            for i in range(len(colors)):
                if colors[i] == menu_bouton_color:
                    menu_bouton_color = colors[(i+1)%len(colors)]
                    break
        elif button_name == "TEXT COLOR":
            colors = ["white", "black", "grey"]
            for i in range(len(colors)):
                if colors[i] == menu_text_color:
                    menu_text_color = colors[(i+1)%len(colors)]
                    break
        elif button_name == "SCREEN WIDTH":
            widths = [1280, 1280//1.25, 1280//1.5]
            for i in range(len(widths)):
                if widths[i] == W:
                    W = widths[(i+1)%len(widths)]
                    #max_horizontal_buttons = round(max_vertical_buttons * (16 / 9))
                    current_buttons = []
                    full_reload()
                    break
                if i == len(widths) - 1:
                    W = widths[0]
        elif button_name == "SCREEN HEIGHT":
            heights = [720, 720//1.25, 720//1.5]
            for i in range(len(heights)):
                if heights[i] == H:
                    H = heights[(i+1)%len(heights)]
                    #max_horizontal_buttons = round(max_vertical_buttons * (16 / 9))
                    current_buttons = []
                    full_reload()
                    break
                if i == len(heights) - 1:
                    H = heights[0]
        elif button_name == "WIDTH INPUT":
            button = find_button("WIDTH INPUT")
            if button.input_mode:
                not_input_mode()
            else:
                not_input_mode()
                button.input_mode = True
                button.input_string = ""
                current_input_mode = True
        elif button_name == "HEIGHT INPUT":
            button = find_button("HEIGHT INPUT")
            if button.input_mode:
                not_input_mode()
            else:
                not_input_mode()
                button.input_mode = True
                button.input_string = ""
                current_input_mode = True
        elif button_name == "BUTTON SIZE":
            sizes = [8, 10, 12, 14]
            for i in range(len(sizes)):
                if sizes[i] == max_vertical_buttons:
                    max_vertical_buttons = sizes[(i+1)%len(sizes)]
                    max_horizontal_buttons = round(max_vertical_buttons * (16 / 9))
                    current_buttons = []
                    break
                if i == len(sizes) - 1:
                    max_vertical_buttons = sizes[0]
            full_reload()
        elif button_name == "BUTTON ZOOM":
            zooms = [1.2, 1.3, 1.4, 1.5]
            for i in range(len(zooms)):
                if zooms[i] == bouton_zoom:
                    bouton_zoom = zooms[(i+1)%len(zooms)]
                    break
                if i == len(zooms) - 1:
                    bouton_zoom = zooms[0]
    elif current_page == 2: # game page
        if button_name == "BACK":
            current_page = 0
    
    reload_page()

def check_events():
    global game, current_buttons, current_input_mode, current_input
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
                    button_handler(button.name)

def frame():
    global W, H, fenetre, game, current_page, current_page_name, current_buttons, changing_page, current_input_mode
    current_page_name = pages_names[current_page]
    last_page = current_page
    pygame.display.set_caption(current_page_name)
    pygame.display.update()
    pygame.draw.rect(fenetre, 'black', (0, 0, W, H))
    if current_page == 0:
        start_menu()
    elif current_page == 1:
        options_menu()
    elif current_page == 2:
        game_page()
    check_events()
    if last_page != current_page:
        changing_page = True
        current_buttons = []
        not_input_mode()
    else:
        changing_page = False

load_data()

while game:
    frame()
    pygame.time.delay(1000//30)

make_data() # if file doesnt exists creates it + saves data

pygame.quit()

# idées/possibilitées :
# - open world (platformer/aventure genre zelda, pokemon...)
# - jeu de stratégie (rts/tower defense/tour par tour)
# - jeu action (roguelite/dungon crawler/hack n slash)
# -> partir sur un jeu strategie tour par tour genre civ 6 (grille hexagonale, 4X, arbre technologie, etc...) ? (en beacoup moins complexe)

# idées d ajouts :
# - menus (exemples : menu de depart, menu options, menus en jeu, mini menus qui ne prennent pas toute la page)
# - sauvegarde
# - mini IA pour les ennemis
# - generation de map (en fonction de type de jeu choisi)

# à faire :
# - essayer d optimiser mon code spaghetti pour eviter trop de lag :) (par exemple j update() les boutons constamment mais je suis quasi sur qu on peut trouver un moyen d eviter cela)
# - faire en sorte que le bouton sur lequel on zoome soit affiché en priorité (donc affiché en dernier pour etre par dessus les autres)
# - essayer de faire un meilleur systeme pour les boutons, avec les avantages de 2_1.py et de 2_2.py (voir section dans "a savoir").
# - pouvoir passer en plein ecran
# - actuellement taille des boutons proportionnelle à H, peut etre la rendre proportionnelle à W ? -> probleme : le texte. quand on change sa taille, c est a la fois x et y. comment faire pour etre proportionnel a W et H sans revenir a 2_1.py ?
# - peut etre modifier classe Button pour pouvoir faire disparaitre certains boutons ? (et empecher d interagir avec)
# - peut etre rendre position de certains boutons relative a celle d autres boutons ? car quand on change la taille des boutons, W ou H, ils peuvent s eloigner ou se rapprocher d autres boutons
# - faire plusieurs files, ne pas tout mettre dans main.py 
# - peut etre changer le full_reload() our faire encore une autre fonction reload pour ne pas avoir l ecran qui clignote en noir quand on l appelle
# - dans button_handler(), remplacer code dans les structures conditionnelles par une fonction pour chaque type de bouton
# - remplacer assets_path par fonction qui recherche son path ? (pour ne pas avoir a le faire manuellement)
# - pour creer systeme grille hexagones : https://www.redblobgames.com/grids/hexagons/
# - ajouter curseurs ? (nouveau type boutons) -> pouvoir deplacer objets en restant appuyé dessus (avec souris) ?

# à savoir :
# - un numero est associé à 1 page : 0 pour start_menu, 1 pour options_menu, 2 pour game
# - les boutons ont beacoup, beacoup de parametres. mais au moins maintenant on peut faire quasiment n importe quel bouton
# - si on veut changer parametres initiaux, le faire dans data/settings.json (car si on le fait au debut du code bugs puisque après remplacé par settings.json)
# - actuellement plus de 500 lignes de code pour juste un petit menu, c est un peu beacoup. mais au moins maintenant il y a une bonne base, pas vrai ? pas vrai...?
#
# - difference entre 2_1.py et 2_2.py (anciennes versions): le systeme d espace entre les boutons. 
#   pour 2_1, le nombre de boutons horizontaux (sur axe x) est proportionnel au nombre de boutons verticaux multipliés par le ratio W/H. 
#       avantage : toujours meme espace entre boutons, leur arrangement ne change pas.
#       desavantage : boutons peuvent sortir de l ecran.
#   pour 2_2, le nombre de boutons horizontaux est proportionnel au nombre de boutons verticaux multipliés par le ratio 16/9. ils ne dépendent plus de la taille de l ecran. 
#       avantage : boutons toujours visibles sur l ecran. 
#       desavantage : espace entre les boutons peut changer, donc certains boutons peuvent en cacher d autres.
