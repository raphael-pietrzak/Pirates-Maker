import pygame
from pygame import Vector2 as vector
from pygame.mouse import get_pos as mouse_pos
from pygame.mouse import get_pressed as mouse_buttons
from imports import import_data, import_data_dict, import_data_folder_dict, save_txt, load_txt
from game_menu import Button, ButtonGroup, Sign
from os import walk
from pygame.image import load
from settings import *


class Overworld:
    def __init__(self, switch):
        self.display_surface = pygame.display.get_surface()
        self.levels_sprites = pygame.sprite.Group()

        self.switch = switch

        self.origin = vector(0, 0)  

        self.node_drag_active = False

        self.imports()
        self.create_nodes()
        self.editor_active = False

        self.buttons = ButtonGroup()
        self.back_button = Button((100, 70),(150, 50), 'Back', self.buttons)

        self.screen_title = Sign((WINDOW_WIDTH-125, 25), (250, 50), 'Overworld', self.buttons)


    def imports(self):
        self.overworld_graphics = {}
        self.overworld_graphics = import_data_folder_dict('../graphics/overworld')

    def create_nodes(self):
        node_pos = load_txt('../Saves/nodes.txt')
        nodes_count = len(self.overworld_graphics) - 3
        for i in range(nodes_count):
            key = f'{i}'
            if key in node_pos:
                Node(node_pos[key], self.levels_sprites, self.overworld_graphics[key], i+1)
            else : 
                Node((70*i, 50*i), self.levels_sprites, self.overworld_graphics[key], i+1)


    # input
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch('Main Menu')

            self.node_drag(event)
            self.save_nodes(event)
            self.level_click(event)
            self.back_click(event)
    
    def back_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
            if self.back_button.rect.collidepoint(mouse_pos()):
                self.switch('Main Menu')
        
        

            
    def save_nodes(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            node_pos = {}
            index = 0
            for node in self.levels_sprites:
                node_pos[index] = node.rect.center
                index += 1
            save_txt('../Saves/nodes.txt', node_pos)
    
    def level_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
            for node in self.levels_sprites:
                if node.rect.collidepoint(mouse_pos()):
                    self.switch('Level', node.get_id())

    def node_drag(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[2]:
            for node in self.levels_sprites:
                if node.rect.collidepoint(mouse_pos()):
                    node.drag_active = True
                    node.offset = vector(node.rect.center) - mouse_pos()
                    self.node_drag_active = True
        
        if event.type == pygame.MOUSEBUTTONUP and self.node_drag_active:
            self.node_drag_active = False
            for node in self.levels_sprites:
                node.drag_active = False


    # drawing
    def draw_node_lines(self):
        sprites = self.levels_sprites.sprites()
        sprites_pos = list(map(lambda sprite: sprite.pos, sprites))
        pygame.draw.lines(self.display_surface, OVERWORLD_LINES, False, sprites_pos, 8)

    def draw_background(self):
        pygame.draw.rect(self.display_surface, OVERWORLD_FG_COLOR, (0, 500, WINDOW_WIDTH, WINDOW_HEIGHT))
        horizon_rect1 = pygame.Rect(0, 500-10, WINDOW_WIDTH,  10)
        horizon_rect2 = pygame.Rect(0, 500-16, WINDOW_WIDTH, 4)
        horizon_rect3 = pygame.Rect(0, 500-20, WINDOW_WIDTH, 2)
        pygame.draw.rect(self.display_surface, OVERWORLD_FG_COLOR, horizon_rect1)
        pygame.draw.rect(self.display_surface, OVERWORLD_FG_COLOR, horizon_rect2)
        pygame.draw.rect(self.display_surface, OVERWORLD_FG_COLOR, horizon_rect3)
        cloud0 = self.overworld_graphics['clouds'][0]
        cloud1 = self.overworld_graphics['clouds'][1]
        cloud2 = self.overworld_graphics['clouds'][2]

        self.display_surface.blit(cloud0, (0, 300))
        self.display_surface.blit(cloud1, (300, 200))
        self.display_surface.blit(cloud2, (800, 100))

        palms = self.overworld_graphics['palms']
        palm0 = palms[0]
        palm1 = palms[1]
        palm2 = palms[2]
        palm3 = palms[3]
        palm4 = palms[4]
        palm5 = palms[5]
        self.display_surface.blit(palm0, (600, 395))
        self.display_surface.blit(palm1, (620, 360))
        self.display_surface.blit(palm2, (640, 410))

        self.display_surface.blit(palm3, (900, 420))

        self.display_surface.blit(palm4, (1180, 392))
        self.display_surface.blit(palm5, (1200, 360))
        

    # update

    def title_update(self):
        title = 'Editor' if self.editor_active else 'Overworld'
        self.screen_title.text = title
        if self.editor_active:
            self.key = Sign((WINDOW_WIDTH - 150, WINDOW_HEIGHT-60), (400, 50), 'Save Key : [s]', self.buttons)
            self.key.draw_text()
        

    def run(self, dt):
        self.title_update()
        self.display_surface.fill(OVERWORLD_BG_COLOR)
        self.draw_background()
        self.levels_sprites.update(dt)
        self.draw_node_lines()
        self.levels_sprites.draw(self.display_surface)
        self.buttons.draw(self.display_surface)
        self.buttons.update()
        self.event_loop()


class Node(pygame.sprite.Sprite):
    def __init__(self, pos, group, frames, node_id):
        super().__init__(group)

        # animation
        self.frame_index = 0
        self.frames = frames
        self.image = self.frames[self.frame_index]

        # position
        self.pos = pos
        self.rect = self.image.get_rect(center = self.pos)
        self.node_id = node_id

        # drag
        self.drag_active = False
        self.offset = vector(0, 0)

    def get_id(self):
        return self.node_id
    
    def drag(self):
        if self.drag_active:
            self.pos = mouse_pos() + self.offset
            self.rect.center = self.pos

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    
    def update(self, dt):
        self.drag()
        self.animate(dt)
    

