import pygame, sys
from pygame import Vector2 as vector
from pygame.mouse import get_pos as mouse_pos
from pygame.mouse import get_pressed as mouse_buttons
from imports import  save_txt, load_settings
from os import walk
from pygame.image import load
from settings import *



# menus
class GameMenu:
    def __init__(self, switch):
        self.display_surface = pygame.display.get_surface()
        self.buttons = ButtonGroup()
        self.create_buttons()
        self.switch = switch

    # input
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.menu_click(event)
        
    def menu_click(self, event):
        if self.buttons.hover:
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
                for sprite in self.buttons:
                    if sprite.rect.collidepoint(mouse_pos()):
                        self.switch(sprite.text)


    # draw
    def create_buttons(self):
        first_pos_y = 300
        margin = 80
        Button((WINDOW_WIDTH/2, first_pos_y), (WINDOW_WIDTH/2, 50), 'Levels', self.buttons)
        Button((WINDOW_WIDTH/2, first_pos_y + margin), (WINDOW_WIDTH/2, 50), 'Editor', self.buttons)
        Button((WINDOW_WIDTH/2, first_pos_y + 2*margin), (WINDOW_WIDTH/2, 50), 'Settings', self.buttons)


    # update
    def run(self, dt):
        self.display_surface.fill('gray')
        self.buttons.draw(self.display_surface)
        self.buttons.update()
        self.buttons.is_hovering()
        self.event_loop()

class SettingsMenu:
    def __init__(self, switch, sound):
        self.display_surface = pygame.display.get_surface()
        self.buttons = ButtonGroup()
        self.signs = pygame.sprite.Group()

        self.sound = sound
        self.sound.play_music(self.sound.explorer)


        self.switch = switch
        self.get_settings()

        self.create_buttons()

    
    def get_settings(self):
        settings = load_settings('../saves/settings.txt')
        self.sound.allowMusic = settings['music']
        self.sound.allowSFX = settings['sfx']
        self.sound.music_channel.pause() if not self.sound.allowMusic else self.sound.music_channel.unpause()



    def create_buttons(self):
        first_pos_y = 300
        margin = 80
        music = 'On' if self.sound.allowMusic else 'Off'
        sfx = 'On' if self.sound.allowSFX else 'Off'

        self.credits_button = Button((WINDOW_WIDTH/2- 300, first_pos_y - margin), (400, 50), 'Credits', self.buttons)
        self.music_button = Button((WINDOW_WIDTH/2 - 300 , first_pos_y), (400, 50),'Music', self.buttons)
        self.sfx_button = Button((WINDOW_WIDTH/2- 300, first_pos_y + margin), (400, 50), 'SFX', self.buttons)
        self.back_button = Button((WINDOW_WIDTH/2- 300, first_pos_y + 2*margin), (400, 50), 'Back', self.buttons)
        self.music_sign = Sign((WINDOW_WIDTH/2 + 100, first_pos_y), (200, 50), music, self.signs)
        self.sfx_sign = Sign((WINDOW_WIDTH/2 + 100, first_pos_y + margin), (200, 50), sfx, self.signs)


    
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch('Main Menu')
            self.menu_click(event)
            self.save_settings()
    
    def save_settings(self):
        settings = {
            'music': self.sound.allowMusic,
            'sfx': self.sound.allowSFX
        }
        save_txt('../saves/settings.txt', settings)

    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
            if self.music_button.rect.collidepoint(mouse_pos()):
                self.music_sign.toggle()
                self.sound.allowMusic = False if self.sound.allowMusic else True
                self.sound.music_channel.pause() if not self.sound.allowMusic else self.sound.music_channel.unpause()
            if self.sfx_button.rect.collidepoint(mouse_pos()):
                self.sfx_sign.toggle()
                self.sound.allowSFX = False if self.sound.allowSFX else True
            if self.back_button.rect.collidepoint(mouse_pos()):
                self.switch('Main Menu')
            if self.credits_button.rect.collidepoint(mouse_pos()):
                self.switch('Credits')
                

    
    def run(self, dt):
        self.display_surface.fill('purple')
        self.buttons.draw(self.display_surface)
        self.signs.draw(self.display_surface)
        self.buttons.update()
        self.signs.update()
        self.event_loop()


# groups
class ButtonGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.hover = False

    def is_hovering(self):
        hover = False
        for sprite in self:
            if sprite.rect.collidepoint(mouse_pos()):
                sprite.is_hovering = True
                hover = True
            else:
                sprite.is_hovering = False
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND) if hover else pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.hover = hover
    
    def update(self):
        self.is_hovering()
        for sprite in self:
            sprite.update()


# components    
class Button(pygame.sprite.Sprite):
    def __init__(self, pos, size, text, group):
        super().__init__(group)
        self.display_surface = pygame.display.get_surface()
        self.pos = pos
        self.text = text
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(center = self.pos)
        self.is_hovering = False
    
    def draw_text(self):
        self.image.fill(BUTTON_BG_COLOR)
        self.font = pygame.font.Font('../graphics/ui/ARCADEPI.TTF',30)

        self.text_surf = self.font.render(self.text, False, 'white')
        self.text_rect = self.text_surf.get_rect(center = self.rect.center)
        self.display_surface.blit(self.text_surf, self.text_rect)

    def hover(self):
        if self.is_hovering:
            outline = self.rect.copy().inflate(10, 10)
            pygame.draw.rect(self.display_surface, 'white', outline, 4, 5)
    
    def update(self):
        self.draw_text()
        self.hover()

class Sign(pygame.sprite.Sprite):
    def __init__(self, pos, size, text, group):
        super().__init__(group)
        self.display_surface = pygame.display.get_surface()
        self.pos = pos
        self.text = text
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(center = self.pos)
        self.font = pygame.font.Font('../graphics/ui/ARCADEPI.TTF',30)

    
    def draw_text(self):
        self.image.fill(BUTTON_BG_COLOR)
        self.text_surf = self.font.render(self.text, False, 'white')
        self.text_rect = self.text_surf.get_rect(center = self.rect.center)
        self.display_surface.blit(self.text_surf, self.text_rect)
    
    def toggle(self):
        self.text = 'On' if self.text == 'Off' else 'Off'

    def update(self):
        self.draw_text()


class EndScreen:
    def __init__(self, switch, level_id, duration, end_message):
        self.display_surface = pygame.display.get_surface()

        self.buttons = ButtonGroup()
        self.signs = pygame.sprite.Group()
        self.switch = switch
        self.duration = duration
        self.level_id = level_id
        self.end_message = end_message

        self.level_max = 6
        

        
        Sign((WINDOW_WIDTH/2, 25), (WINDOW_WIDTH, 50), f'Level {self.level_id}', self.signs)
        self.end_sign = Sign((WINDOW_WIDTH/2, 85), (800, 70), self.end_message, self.signs)
        self.end_sign.font = pygame.font.Font('../graphics/ui/ARCADEPI.TTF',70)



        minutes, seconds = divmod(self.duration/1000, 60)
        self.time = f'Time : {int(minutes)} min {seconds} sec'
        Sign((WINDOW_WIDTH/2, 330), (WINDOW_WIDTH/2, 50), self.time, self.signs)
        Sign((WINDOW_WIDTH/2, 410), (WINDOW_WIDTH/2, 50), 'Coins : 33', self.signs)
        button_margin = 20
        self.play_again_button = Button((WINDOW_WIDTH/2 - WINDOW_WIDTH/8- button_margin/2 , 490), (WINDOW_WIDTH/4 - button_margin, 50), 'Play Again', self.buttons)
        if self.end_message == 'Victory' and level_id<self.level_max:
            self.next_button = Button((WINDOW_WIDTH/2 + WINDOW_WIDTH/8+ button_margin/2, 490), (WINDOW_WIDTH/4 - button_margin, 50), 'Next', self.buttons)
            self.back_button = Button((WINDOW_WIDTH/2, 570), (WINDOW_WIDTH/2, 50), 'Back', self.buttons)
        else:
            self.back_button = Button((WINDOW_WIDTH/2 + WINDOW_WIDTH/8+ button_margin/2, 490), (WINDOW_WIDTH/4 - button_margin, 50), 'Back', self.buttons)

    
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch('Levels')
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
                if self.play_again_button.rect.collidepoint(mouse_pos()):
                    self.switch('Level', self.level_id)
                if self.back_button.rect.collidepoint(mouse_pos()):
                    self.switch('Levels')
                if self.level_id < self.level_max and self.end_message == 'Victory' and self.next_button.rect.collidepoint(mouse_pos()):
                    self.switch('Level', self.level_id + 1)
                

    def run(self, dt):
        self.display_surface.fill('green')
        self.event_loop()
        self.buttons.draw(self.display_surface)
        self.buttons.update()
        self.signs.draw(self.display_surface)
        self.signs.update()


class Credits:
    def __init__(self, switch):
        self.display_surface = pygame.display.get_surface()

        self.buttons = ButtonGroup()
        self.back_button = Button((100, 70),(150, 50), 'Back', self.buttons)
        Sign((WINDOW_WIDTH/2, WINDOW_HEIGHT/2), (900, WINDOW_HEIGHT), '', self.buttons)
        Sign((WINDOW_WIDTH/2, 200), (WINDOW_WIDTH/2, 50), 'Game Credits:', self.buttons)
        Sign((WINDOW_WIDTH/2, 300), (WINDOW_WIDTH/2, 50), 'Inspired by: Clear Code (YT)', self.buttons)
        Sign((WINDOW_WIDTH/2, 350), (WINDOW_WIDTH/2, 50), 'Game made by: Raphael Pietrzak', self.buttons)
        Sign((WINDOW_WIDTH/2, 400), (WINDOW_WIDTH/2, 50), 'Artwork by: Pixelfrog', self.buttons)
        Sign((WINDOW_WIDTH/2, 450), (WINDOW_WIDTH/2, 50), 'Music by: opengameart.org', self.buttons)
    
        self.switch = switch

    
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch('Settings')
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
                if self.back_button.rect.collidepoint(mouse_pos()):
                    self.switch('Settings')
    
    def run(self, dt):
        self.display_surface.fill('gray')
        self.event_loop()
        self.buttons.draw(self.display_surface)
        self.buttons.update()

            
