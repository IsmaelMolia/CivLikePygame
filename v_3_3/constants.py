import math

# assets
ASSETS_PATH = "4_pygame/assets"
#CURSOR_FILEPATH = f"{ASSETS_PATH}/cursors/without_outline"
CURSOR_FILEPATH = f"{ASSETS_PATH}/cursors/with_outline"
CURSORS_FILEPATHS = {"default":f"{CURSOR_FILEPATH}/pointer_scifi_b.png", "build":f"{CURSOR_FILEPATH}/tool_hammer.png", "city":f"{CURSOR_FILEPATH}/cursor_cogs.png", "unit":f"{CURSOR_FILEPATH}/target_round_a.png", "building":f"{CURSOR_FILEPATH}/tool_wrench.png", "build":f"{CURSOR_FILEPATH}/tool_hammer.png", "moving":f"{CURSOR_FILEPATH}/steps.png"}
UNITS_FILEPATHS = {"unit":None, "settler":f"{ASSETS_PATH}/units/settler.png", "city":f"{ASSETS_PATH}/units/castle.png"}
RESSOURCES_PATH = f"{ASSETS_PATH}/ressources"
RESSOURCES_FILEPATHS = {"food":f"{RESSOURCES_PATH}/apple_1.png", "wood":f"{RESSOURCES_PATH}/wood_2.png", "rock":f"{RESSOURCES_PATH}/rock_1.png", "gold":f"{RESSOURCES_PATH}/coins_2.png", "horse":f"{RESSOURCES_PATH}/horse_2.png", "iron":f"{RESSOURCES_PATH}/iron_3.png", "mana_cristal":f"{RESSOURCES_PATH}/mana_cristal_1.png"} # à mettre dans l ordre d affichage
BUILDINGS_PATH = f"{ASSETS_PATH}/buildings"
BUILDINGS_FILEPATHS = {"farm":f"{BUILDINGS_PATH}/building_wheat.png", "windmill":f"{BUILDINGS_PATH}/building_windmill.png", "woodcutter":f"{BUILDINGS_PATH}/building_lumberjack.png", "quarry":f"{BUILDINGS_PATH}/building_mine_copper.png", "market":f"{BUILDINGS_PATH}/building_marketplace.png"}

# écran
W, H = 1280, 720
MIN_W, MIN_H = W//2, H//2
MAX_W, MAX_H = round(W * 1.2), round(H * 1.2)

# boutons
VERTICAL_HORIZONTAL_RATIO = (16 / 9)
MAX_VERTICAL_BUTTONS = 10
MAX_HORIZONTAL_BUTTONS = round(MAX_VERTICAL_BUTTONS * VERTICAL_HORIZONTAL_RATIO)
BUTTON_ZOOM = 1.2
BUTTON_ROUNDNESS = 10
BUTTON_DEFAULT_BACKGROUND_COLOR = "purple"
BUTTON_DEFAULT_TEXT_COLOR = "white"
COLOR_BUTTON_ACTIVATED = {False:"red", True:"green"} # actuellement seulement utile pour 3 boutons

# ui
PAUSE_COLOR = "black"
UI_COLOR = (45, 50, 60)
UI_ROUNDNESS = 20
SIDE_PAGES_COLORS = { # un peu inutile car seulement COMMANDS a une couleur differente
    "COMMANDS":"black",
    "UI":UI_COLOR,
    "BUILD":UI_COLOR,
    "MINIMAP":UI_COLOR,
    "TILE":UI_COLOR,
    "CURRENT_UNIT":UI_COLOR,
    "CURRENT_BUILDING":UI_COLOR,
    "CURRENT_CITY":UI_COLOR,
    "INSPECT":UI_COLOR,
    "HELP_TEXT":UI_COLOR
}

# sauvegardes
MIN_SAVE = 1
MAX_SAVE = 10

# taille tiles
TILE_NUMBER_FACTOR = 1.75
INITIAL_TILE_NUMBER_FACTOR = TILE_NUMBER_FACTOR
TILES_COLUMNS = round(16 * TILE_NUMBER_FACTOR)
TILE_HORIZONTAL_SPACE = W / TILES_COLUMNS
TILE_VERTICAL_SPACE = (TILE_HORIZONTAL_SPACE / math.sqrt(3)) * (3/2)
TILES_LINES = round(H / TILE_VERTICAL_SPACE)

# tiles
TILES_COLORS = { # fait avec IA car manque d inspiration au niveau esthetique :/
    "empty":    (235, 235, 235),  # blanc cassé
    "plain":    (120, 200, 60),   # vert vif
    "water":    (50, 140, 255),   # bleu lumineux
    "mountain": (110, 110, 110),  # gris roche
    #"mountain": (200, 200, 200),
    "forest":   (20, 140, 40),    # vert forêt saturé
    "hill":     (190, 140, 50)    # brun doré
    #"hill":     (110, 110, 110) 
}
TILE_BACKGROUND_COLOR = (80, 60, 40) # aussi IA
FOG_OF_WAR_TILE_COLOR = (60, 60, 60)
FOG_OF_WAR_BACKGROUND_COLOR = (0, 0, 0)
NORMAL_RESSOURCES = {"empty":[], "plain":["food", "food"], "water":["food"], "mountain":["rock", "rock"], "forest":["food", "wood"], "hill":["rock"]}
PROD_PER_RESSOURCE = {"food":0.5, "wood":1, "rock":1.5}

# generation tiles
TILES_PROBABILITIES = {"empty":0, "plain":30, "water":10, "mountain":15, "forest":25, "hill":20} # completement arbitraire :)
INTERVALS_TILES_PROBABILITIES = {"empty":[0, 0], "plain":[1, 100], "water":[0, 100], "mountain":[0, 100], "forest":[0, 100], "hill":[0, 100]} # arbitraire aussi :)
BIOMES_SIZES_INTERVALS = {"empty":[1, 1], "plain":[7, 20], "water":[2, 10], "mountain":[4, 8], "forest":[3, 15], "hill":[5, 7]} # arbitraire aussi :)
PRINT_TOTAL_TILES = False # mettre True si on veut print dans la console le nombre total de tiles

# map
MIN_LAYERS = 1 # sinon bugs ? 
MAX_LAYERS = 30

# zoom camera
MIN_FACTOR = 0.75
MAX_FACTOR = 5
CHANGING_SIZE_SPEED = 20 # higher number = slower

# players
MIN_PLAYER_NUMBER = 1
MAX_PLAYER_NUMBER = 4
PLAYERS_COLORS = ["red", "blue", "green", "yellow", "purple", "orange"]
BIG_SPAWN = True # si False, city créée avec 1 case. si True, city créée avec 7 cases.

# units 
USUAL_TILES_NOT_ALLOWED = ["water", "mountain"]
UNITS_TILES_NOT_ALLOWED = {"unit":USUAL_TILES_NOT_ALLOWED, "settler":USUAL_TILES_NOT_ALLOWED}
TILES_MOVEMENT_COST = {"empty":0, "plain":1, "water":0.5, "mountain":2, "forest":1.5, "hill":1.5}
UNITS_INCOME = {"unit":{}, "settler":{}, "city":{"gold":5}}
UNITS_UPKEEP_COST = {"unit":{"food":1}, "settler":{"food":1}, "city":{}}
UNITS_STATS = {
    "unit":{"movement":0, "damage":0, "hp":1, "prod":0, "size_constant":1},
    "settler":{"movement":3, "damage":2, "hp":10, "prod":0, "size_constant":1.2},
    "city":{"movement":0, "damage":5, "hp":100, "prod":5, "size_constant":1}
}

# sides buttons et UI
SMALLEST_SIZE = 0.45
SMALLER_SIZE = 0.6
SLIGHTLY_SMALLER_SIZE = 0.8
SLIGHTLY_BIGGER_SIZE = 1.2
SMALLEST_SPACE = 0.55
SMALLER_SPACE = 0.675
COMMANDS_DECALAGE = 0.5
UI_INITIAL_DECALAGE_X = 1.3
UI_DECALAGE_X = 2
UI_DECALAGE_RESSOURCES_STRAT = 1
UI_DECALAGE_INCOME = 0.55
UI_DECALAGE_Y = 0.35
UI_SPACE = 2
ICON_DECALAGE_INCOME = 0.5
ICON_SIZE = 0.5

# icones buildings pour menu build
BUILD_ICON_SIZE = 0.75
BUILD_ICONS_HORIZONTAL_DECALAGE = 14.8 - SMALLEST_SPACE * 4
BUILD_ICONS_VERTICAL_DECALAGE = 0.75 + 3.125 * SMALLER_SPACE
BUILD_ICONS_HORIZONTAL_SPACE = SMALLEST_SPACE * 3
BUILD_ICONS_VERTICAL_SPACE = SMALLER_SPACE * 2
BUILD_ICONS_POSITIONS = {"farm":(0, 0), "windmill":(1, 0), "woodcutter":(0, 1), "quarry":(0, 2), "market":(0, 3)}

# affichage vision ressources
RESSOURCE_SIZE = 0.75
RESSOURCE_VERTICAL_DECALAGE = 0.25

# inspect
DEACTIVATE_INSPECT_IF_NOT_UNIT_AND_BUILDING = False # mettre True pour désactiver INSPECT quand UNIT ou BUILDING et désactivé et que l'autre l'est aussi (ex : désactiver UNIT sans réactiver BUILDING désactivera INSPECT)
TYPES = ["type : tile", "type : unit", "type : building"]
def get_ressources_text(ressources):
    text = ""
    for i in range(len(ressources)):
        text += ressources[i]
        if i+1 < len(ressources):
            text += ", "
    if text == "":
        return "None"
    return text
def get_income_or_outcome_text(income_or_ouctome):
    text = ""
    i = 0
    for key, value in income_or_ouctome.items():
        text += f"{value}x {key}"
        if i+1 < len(income_or_ouctome):
            text += ", "
        i += 1
    if text == "":
        return "None"
    return text
def get_tile_prod(tile_type):
    prod = 0
    for r in NORMAL_RESSOURCES[tile_type]:
        prod += PROD_PER_RESSOURCE[r]
    return prod
INSPECT_DATA = { # chacun doit avoir 6 textes pour effacer les autres textes quand il les remplace
    "empty":["EMPTY", TYPES[0], "this tile shouldn't be in the game", " ", " ", " "],
    "plain":["PLAIN", TYPES[0], f"ressources : {get_ressources_text(NORMAL_RESSOURCES["plain"])}", "strategic ress : None", f"prod : {get_tile_prod("plain")}"],
    "water":["WATER", TYPES[0], f"ressources : {get_ressources_text(NORMAL_RESSOURCES["water"])}", "strategic ress : None", f"prod : {get_tile_prod("water")}"],
    "mountain":["MOUNTAIN", TYPES[0], f"ressources : {get_ressources_text(NORMAL_RESSOURCES["mountain"])}", "strategic ress : None", f"prod : {get_tile_prod("mountain")}"],
    "forest":["FOREST", TYPES[0], f"ressources : {get_ressources_text(NORMAL_RESSOURCES["forest"])}", "strategic ress : None", f"prod : {get_tile_prod("forest")}"],
    "hill":["HILL", TYPES[0], f"ressources : {get_ressources_text(NORMAL_RESSOURCES["hill"])}", "strategic ress : None", f"prod : {get_tile_prod("hill")}"],
    "settler":["SETTLER", TYPES[1], "special action : create city", f"damage : {UNITS_STATS["settler"]["damage"]}", f"income : {get_income_or_outcome_text(UNITS_INCOME["settler"])}", f"outcome : {get_income_or_outcome_text(UNITS_UPKEEP_COST["settler"])}"],
    "city":["CITY", TYPES[2], f"income : {get_income_or_outcome_text(UNITS_INCOME["city"])}", f"ouctome : {get_income_or_outcome_text(UNITS_UPKEEP_COST["city"])}", f"building prod : {UNITS_STATS["city"]["prod"]}", " "]
}

# city expansion
BASE_EXPANSION_FOOD_NEEDED = 15
FOOD_NEED_ADDED_PER_NEW_TILE = 15
MAXIMUM_TILES_PER_CITY = 15
