
import pygame
from sprites import Generic
from pygame import Vector2 as vector
from settings import *

class Wallet(Generic):
    def __init__(self, pos, surf, group):
        super().__init__(pos, surf, group)
        self.display_surface = pygame.display.get_surface()
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.coins = 0

    
    def draw_coins(self):
        self.font = pygame.font.Font('../graphics/ui/ARCADEPI.TTF',30)
        self.text_surf = self.font.render(str(self.coins), False, 'black')
        self.text_rect = self.text_surf.get_rect(midleft = self.rect.center + vector(20, 0))
        self.display_surface.blit(self.text_surf, self.text_rect)

    def update(self, dt):
        self.draw_coins()   
    

class HealthBar(Generic):
    def __init__(self, pos, surf, group):
        super().__init__(pos, surf, group)
        self.display_surface = pygame.display.get_surface()
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.max_health = 100
        self.health = 100

    def draw_health(self):
        max_health_pixels = 149
        health_pixels = int(self.health / self.max_health * max_health_pixels)
        health_start = (self.rect.topleft[0] + 34, self.rect.topleft[1] + 30)
        health_end = (health_start[0] + health_pixels, health_start[1])
        pygame.draw.line(self.display_surface, HEALTH_COLOR, health_start, health_end, 5)

    def update(self, dt):
        self.draw_health()