import pygame
import json
import os

pygame.init() # important pour les Font

# variables au choix début

W, H = 1280, 720
max_vertical_buttons = 10 # je recommande 10 (en dessous problèmes de décalage et au dessus boutons trop petits)
max_horizontal_buttons = round(max_vertical_buttons * (W / H))
menu_bouton_color = "purple" # environ (175, 0, 255) ?
menu_text_color = "white" # (255, 255, 255)
bouton_zoom = 1.2 # je recommande 1.2 (facteur de zoom quand on passe sa souris sur un bouton) 
                  # (eviter de mettre en dessous de 1 sinon bugs de collision car la souris n est plus dessus quand rétrécit, donc se rétércit et s aggrandit en boucle)
arrondissement_bords_boutons = 10 # je recoomande 10 ou 15 (-1 ou moins pour ne pas en avoir)
data_filepath = "4_pygame/data/donnees.json"

# variables au choix fin

fenetre = pygame.display.set_mode((W,H))
game = True
initial_json_data = {"current_page":0, "current_specific_buttons":{}, "current_text_zones":{}, "menu_bouton_color":"purple"}
json_data = {}
current_page = 0 # 0 pour start_menu, 1 pour options_menu, 2 pour game 
current_collisions = {}
reload_page = False
input_mode = False
current_input = ""

def set_json_variables():
    global json_data, current_page, menu_bouton_color
    try:
        current_page = json_data["current_page"]
        menu_bouton_color = json_data["menu_bouton_color"]
    except Exception as e:
        print(e)

def load_json(filepath=data_filepath):
    global initial_json_data, json_data, current_page, menu_bouton_color
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(f"{dir_path}/data"):
        os.makedirs(f"{dir_path}/data")
    filepath=f"{dir_path}/data/donnees.json"
    try:
        with open (filepath, "r") as f:
            json_data = json.load(f)
            set_json_variables()
    except FileNotFoundError as e:
        with open (filepath, "w") as f:
            json.dump(initial_json_data, f)
        with open (filepath, "r") as f:
            json_data = json.load(f)
            set_json_variables()

load_json()

def clear_json(filepath=data_filepath):
    global initial_json_data
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(f"{dir_path}/data"):
        os.makedirs(f"{dir_path}/data")
    filepath=f"{dir_path}/data/donnees.json"
    with open (filepath, "w") as f:
        json.dump(initial_json_data, f)

def save_with_json(filepath=data_filepath):
    global json_data, current_page, menu_bouton_color
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(f"{dir_path}/data"):
        os.makedirs(f"{dir_path}/data")
    filepath=f"{dir_path}/data/donnees.json"
    #json_data["current_page"] = current_page # mettre si on veut afficher la page affichée au moment où on avait quitté
    json_data["menu_bouton_color"] = menu_bouton_color
    with open (filepath, "w") as f:
        json.dump(json_data, f)

def draw_button_grid(vertical=max_vertical_buttons, horizontal=max_horizontal_buttons, line_width=(H // max_vertical_buttons)//5-max_vertical_buttons): # grillage pas parfait donc normal si leger decalage avec boutons (je crois)
    if line_width < 1:
        line_width = 1
    for a in range(vertical):
        pygame.draw.line(fenetre, "white", (0, round(a*(H / vertical))), (W, round(a*(H / vertical))), line_width)
    for b in range(horizontal):
        pygame.draw.line(fenetre, "white", (round(b*(W / horizontal)), 0), (round(b*(W / horizontal)), H), line_width)

def specific_button(text, column=max_horizontal_buttons/2, line=max_vertical_buttons/2, size_factor=1, color=menu_bouton_color, text_color=menu_text_color, roundness=arrondissement_bords_boutons):
    font_size = round((H // max_vertical_buttons))
    font = pygame.font.Font(None, round(font_size * size_factor))
    button = font.render(text, True, text_color)
    size = font.size(text)
    background_size_factor = 1.1 # pour que les bords du bouton ne touchent pas le texte

    position_background = (round(column * font_size - (size[0] * background_size_factor) / 2), round(line * font_size - (size[1] * background_size_factor) / 2))
    position_text = (round(column * font_size - size[0] / 2), round(line * font_size - size[1] / 2))
    background = pygame.Rect(position_background[0], position_background[1], round(size[0] * background_size_factor), round(size[1] * background_size_factor))

    pygame.draw.rect(fenetre, color, background, border_radius=roundness)
    fenetre.blit(button, position_text)

    return background

def make_specific_buttons(buttons):
    buttons_dict = {}
    for key, value in buttons.items():
        buttons_dict[key] = specific_button(value["text"], value["pos"][0], value["pos"][1], value["current_size"], value["color"]) # lie le nom du bouton à une zone de collision (un pygame.Rect)
    return buttons_dict

def button_to_input_zone(button:dict):
    global input_mode, current_input
    try:
        button["text"] = current_input
        button["color"] = "black"
        input_mode = True
    except Exception as e:
        print("data not dound")

def check_mouse_collision_with_rect(collision:pygame.Rect):
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()
    if mouse_clicked[0] and collision.collidepoint(mouse_pos):
        return True
    return False

def check_hover_mouse(collisions:dict, specific_buttons:dict):
    #global current_collisions
    for button_name, collision in collisions.items():
        if collision.collidepoint(pygame.mouse.get_pos()):
            if button_name in specific_buttons.keys():
                specific_buttons[button_name]["current_size"] = specific_buttons[button_name]["base_size"] * bouton_zoom
        else:
            if button_name in specific_buttons.keys():
                specific_buttons[button_name]["current_size"] = specific_buttons[button_name]["base_size"]
    return specific_buttons

def menu_button_handler(button_name:str):
    global json_data, game, current_page, menu_bouton_color, current_input, reload_page, input_mode
    if current_page == 0:
        if button_name == "START":
            current_page = 2
        elif button_name == "OPTIONS":
            current_page = 1
        elif button_name == "EXIT":
            game = False
        else:
            print("button not found", current_page, button_name)
    elif current_page == 1:
        if button_name == "BACK":
            current_page = 0
        elif button_name == "BUTTON COLOR":
            colors = ["purple", "blue", "red", "orange", "yellow", "green"]
            for i in range(len(colors)):
                if colors[i] == menu_bouton_color:
                    menu_bouton_color = colors[(i+1)%len(colors)]
                    json_data["menu_bouton_color"] = menu_bouton_color
                    reload_current_page()
                    break
        elif button_name == "SCREEN SIZE":
            reload_current_page()
            input_mode = True
            new_button = json_data["current_specific_buttons"]["SCREEN SIZE"].copy()
            new_button["text"] = " " + current_input
            new_button["color"] = "black"
            json_data["current_specific_buttons"]["SCREEN SIZE"] =  new_button # a remplacer par une zone d input
        else:
            print("button not found", current_page, button_name)
    elif current_page == 2:
        if button_name == "BACK": # temporaire
            current_page = 0
        else:
            print("button not found", current_page, button_name)
    else:
        print("page not found")

def menu(specific_buttons:dict, text_zones={}):
    global json_data, current_page
    #draw_button_grid() # temporaire, pour s aider a placer les boutons
    text = make_specific_buttons(text_zones)
    collisions = make_specific_buttons(specific_buttons)
    specific_buttons = check_hover_mouse(collisions, specific_buttons)
    json_data["current_specific_buttons"] = specific_buttons
    return specific_buttons, collisions

def reload_current_page():
    global current_page, reload_page
    reload_page = True
    frame()

def start_menu_page():
    global json_data, current_collisions, reload_page
    page = 0
    background_0 = pygame.image.load("./4_pygame/assets/Nature Landscapes Free Pixel Art/nature_8/origbig.png")
    background_0 = pygame.transform.scale(background_0, (W, H)) 
    fenetre.blit(background_0, (0, 0))

    specific_buttons = json_data["current_specific_buttons"]
    if specific_buttons == {} or json_data["current_page"] != page or reload_page:
        json_data["current_page"] = page
        specific_buttons = {"START":{"text":"START", "pos":(max_horizontal_buttons//2, max_vertical_buttons//2 - 1), "base_size":1, "current_size":1, "color":json_data["menu_bouton_color"]}, 
                            "OPTIONS":{"text":"OPTIONS", "pos":(max_horizontal_buttons//2, max_vertical_buttons//2), "base_size":1, "current_size":1, "color":json_data["menu_bouton_color"]}, 
                            "EXIT":{"text":"EXIT", "pos":(max_horizontal_buttons//2, max_vertical_buttons//2 + 1), "base_size":1, "current_size":1, "color":json_data["menu_bouton_color"]}}
        
    text_zones = json_data["current_text_zones"]
    if text_zones == {} or json_data["current_page"] != page or reload_page:
        json_data["current_page"] = page
        text_zones = {"START MENU":{"text":"START MENU", "pos":(max_horizontal_buttons//2, 1), "base_size":1.3, "current_size":1.3, "color":"blue"}}
    
    specific_buttons, current_collisions = menu(specific_buttons, text_zones)

def options_menu_page():
    global json_data, current_collisions, reload_page
    page = 1
    background_0 = pygame.image.load("./4_pygame/assets/Nature Landscapes Free Pixel Art/nature_8/origbig.png")
    background_0 = pygame.transform.scale(background_0, (W, H)) 
    fenetre.blit(background_0, (0, 0))

    specific_buttons = json_data["current_specific_buttons"]
    if specific_buttons == {} or json_data["current_page"] != page or reload_page:
        json_data["current_page"] = page
        specific_buttons = {"BUTTON COLOR":{"text":"BUTTON COLOR", "pos":(max_horizontal_buttons//2, max_vertical_buttons//2), "base_size":1, "current_size":1, "color":json_data["menu_bouton_color"]},
                            "BACK":{"text":"BACK", "pos":(max_horizontal_buttons//2, max_vertical_buttons - 1), "base_size":1, "current_size":1, "color":json_data["menu_bouton_color"]},
                            "SCREEN SIZE":{"text":"SCREEN SIZE", "pos":(max_horizontal_buttons//2, max_vertical_buttons//2 - 1), "base_size":1, "current_size":1, "color":json_data["menu_bouton_color"]}}
        
    text_zones = json_data["current_text_zones"]
    if text_zones == {} or json_data["current_page"] != page or reload_page:
        json_data["current_page"] = page
        text_zones = {"OPTIONS MENU":{"text":"OPTIONS MENU", "pos":(max_horizontal_buttons//2, 1), "base_size":1.3, "current_size":1.3, "color":"blue"}}
    
    specific_buttons, current_collisions = menu(specific_buttons, text_zones)

def game_page():
    global json_data, current_collisions, reload_page
    page = 2
    background_0 = pygame.image.load("./4_pygame/assets/Nature Landscapes Free Pixel Art/nature_8/origbig.png")
    background_0 = pygame.transform.scale(background_0, (W, H)) 
    fenetre.blit(background_0, (0, 0))

    specific_buttons = json_data["current_specific_buttons"]
    if specific_buttons == {} or json_data["current_page"] != 2 or reload_page:
        json_data["current_page"] = 2
        specific_buttons = {"BACK":{"text":"BACK", "pos":(max_horizontal_buttons//2, max_vertical_buttons//2), "base_size":1, "current_size":1, "color":json_data["menu_bouton_color"]}}

    text_zones = json_data["current_text_zones"]
    if text_zones == {} or json_data["current_page"] != page or reload_page:
        json_data["current_page"] = page
        text_zones = {"GAME":{"text":"START", "pos":(max_horizontal_buttons//2, 1), "base_size":1.3, "current_size":1.3, "color":"blue"}}
    
    specific_buttons, current_collisions = menu(specific_buttons, text_zones)

def check_events():
    global game, current_collisions, input_mode, current_input
    for event in pygame.event.get():
        if input_mode == True:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    current_input = current_input[:-1]
                elif event.key == pygame.K_RETURN:
                    input_mode = False
                    current_input = ""
                else:
                    current_input += event.unicode
                print(current_input)
        if event.type == pygame.QUIT:
            game = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            input_mode = False
            for button_name, collision in current_collisions.items():
                if check_mouse_collision_with_rect(collision):
                    menu_button_handler(button_name)

def frame():
    global current_page, current_collisions, reload_page, input_mode
    pygame.display.update()
    pygame.draw.rect(fenetre, 'black', (0, 0, W, H))
    if current_page == 0:
        start_menu_page()
    elif current_page == 1:
        options_menu_page()
    elif current_page == 2:
        game_page()
    check_events()
    if input_mode != True:
        reload_page = False

while game:
    frame()
    pygame.time.delay(1000//30)

save_with_json()

pygame.quit()

# idées/possibilitées :
# - open world (platformer/genre pokemon)
# - jeu de stratégie (rts/tower defense/tour par tour)
# - jeu action (roguelite/dungon crawler/hack n slash)

# idées d ajouts :
# - menus (exemples : menu de depart, menu options, menus en jeu)
# - sauvegarde
# - mini IA pour les ennemis
# - generation de map (en fonction de type de jeu choisi)

# à faire :
# - faire en sorte de ne pas avoir à recalculer toutes les variables a chaque fois qu on affiche les boutons ?
# - trouver comment faire pour montrer seulement une partie d une map (exemple : pouvoir faire defiler le paysage, pouvoir zoomer/dezoomer pour regarder la carte)
# - ajouter assets
# - reussir a prendre des inputs dans le menu des options, peut etre pouvoir changer les "variables au choix"
# - changer backgrounds en fonction de type de jeu choisi
# - faire differentes fonctions pour differents types de boutons ?
# - organiser fonctions dans le bon ordre
# - faire differents fichiers json pour differentes donnees (exmpemples : settings, sauvegardes, etc...)
# - pour les fichiers json, faire en sorte que le filepath soit obtenu automatiquement et non manuellement (peut etre meme creer dossier si necessaire) + pareil pour certains assets (ou au moins une partie du filepath)
# - complétement refaire système boutons, utiliser une classe (voir tout refaire depuis le début pour mieux organiser)

# si jeu strategie tour par tour :
# - trouver comment faire une grille d hexagones (forme nid d abeille) simples, sans utiliser de maths trop complexes (pas comme dans "hexagon_grid_test.py")

# à savoir :
# - un numero est associé à 1 page : 0 pour start_menu, 1 pour options_menu, 2 pour game
# - les zones de textes sont juste des boutons qui ne reagissent pas
