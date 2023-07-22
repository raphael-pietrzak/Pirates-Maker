import pygame
from settings import *
from overworld import Overworld
from game_menu import GameMenu
from editor import Editor
from level import Level
from sound import Sound
from game_menu import SettingsMenu, EndScreen, Credits
from pygame.image import load
from imports import import_data, import_data_dict, load_txt
from pygame import Vector2 as vector
from os import walk


class Main:
    def __init__(self):
        pygame.init()
  
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('PIRATES MAKER')
        self.imports()


        # sound
        self.sound = Sound()

        # current screen
        self.overworld = Overworld(self.switch)
        self.game_menu = GameMenu(self.switch)
        self.settings_menu = SettingsMenu(self.switch, self.sound)

        self.current_screen = self.game_menu
        self.editor_active = False



        # clock
        self.clock = pygame.time.Clock()

    def get_level(self, level_id):

        asset_dict = {
            'land': self.land_tiles,
            'water bottom': self.water_bottom,
            'water top': self.water_top_animation,
            'gold': self.gold_animation,
            'silver': self.silver_animation,
            'diamond': self.diamond_animation,
            'particle': self.particle_animation,
            'spikes': self.spikes,
            'tooth': self.tooth_animations,
            'shell': self.shell_animations,
            'palm': self.palm_animations,
            'player': self.player_animations,
            'pearl': self.pearl,
            'clouds': self.clouds,
            'end': self.end
        }


        grid = load_txt(f'../saves/level{level_id}.txt')
        if not grid:
            grid = {
                'water': {},
                'terrain': {},
                'coins': {},
                'enemies': {},
                'bg palms': {},
                'fg objects': {(406, 331): 0, (882, 340): 1}
            }

        return Level(grid, self.switch, asset_dict, self.sound, level_id)

    def switch(self, screen_title, level_id=None, duration=None, end_message=None):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        match screen_title:
            case 'Level' : 
                if self.editor_active:
                    self.current_screen = Editor(self.land_tiles, self.switch, level_id)
                else:
                    self.current_screen = self.get_level(level_id)
            case 'Levels': 
                self.current_screen = self.overworld
                self.overworld.editor_active = False
            case 'Editor': 
                self.overworld.editor_active = True
                self.current_screen = self.overworld
                self.editor_active = True
            case 'Main Menu': 
                self.current_screen = self.game_menu
                self.editor_active = False
            case 'Settings': self.current_screen = self.settings_menu
            case 'End': self.current_screen = EndScreen(self.switch, level_id, duration, end_message)
            case 'Credits' : self.current_screen = Credits(self.switch)
        
    def imports(self):
		# terrain
        self.land_tiles = import_data_dict('../graphics/terrain/land')
        self.water_bottom = load('../graphics/terrain/water/water_bottom.png').convert_alpha()
        self.water_top_animation = import_data('../graphics/terrain/water/animation')
        self.end = load('../graphics/terrain/phase/end.png').convert_alpha()

        # coins
        self.gold_animation = import_data('../graphics/items/gold')
        self.silver_animation = import_data('../graphics/items/silver')
        self.diamond_animation = import_data('../graphics/items/diamond')

        self.particle_animation = import_data('../graphics/items/particle')

        # palm
        self.palm_animations = {f'{file}': import_data(f'../graphics/terrain/palm/{file}') for file in list(walk('../graphics/terrain/palm'))[0][1]}


        # enemies
        self.spikes = load('../graphics/enemies/spikes/spikes.png').convert_alpha()
        self.tooth_animations = {f'{file}': import_data(f'../graphics/enemies/tooth/{file}') for file in list(walk('../graphics/enemies/tooth'))[0][1]}
        self.shell_animations = {f'{file}': import_data(f'../graphics/enemies/shell_left/{file}') for file in list(walk('../graphics/enemies/shell_left'))[0][1]}

        # player
        self.player_animations = {f'{file}': import_data(f'../graphics/player/{file}') for file in list(walk('../graphics/player'))[0][1]}

        self.pearl = load('../graphics/enemies/pearl/pearl.png')

        self.clouds = import_data('../graphics/clouds')

    def run(self):
        while True:
            dt = self.clock.tick() / 1000
            self.current_screen.run(dt)
            pygame.display.update()



if __name__ == '__main__':
    main = Main()
    main.run()