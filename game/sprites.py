from typing import Any
import pygame
from pygame import Vector2 as vector
from settings import *
from stopwatch import Stopwatch
from random import choice, randint

# Generic
class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, group, z=LEVEL_LAYERS['main']):
        super().__init__(group)
        self.z = z
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)

class Cloud(Generic):
    def __init__(self, pos, surf, group, left_limit):
        super().__init__(pos, surf, group, LEVEL_LAYERS['clouds'])
        self.speed = randint(30, 50)
        self.pos = vector(self.rect.topleft)
        self.left_limit = left_limit


    def update(self, dt):
        self.pos.x -= self.speed * dt
        if self.pos.x < self.left_limit:
            self.kill()
        self.rect.topleft = self.pos

class Block(Generic):
    def __init__(self, pos, size, group):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, group)


# Simple animated sprites
class Animated(Generic):
    def __init__(self,assets, pos, group, z=LEVEL_LAYERS['main']):
        self.animation_frames = assets
        self.frame_index = 0
        super().__init__(pos, self.animation_frames[self.frame_index], group, z)
    
    def animate(self, dt):
        self.frame_index += dt * ANIMATION_SPEED
        if self.frame_index >= len(self.animation_frames):
            self.frame_index = 0
        self.image = self.animation_frames[int(self.frame_index)]
        
    def update(self, dt):
        self.animate(dt)

class Coin(Animated):
    def __init__(self, coin_type, assets, pos, group):
        self.coin_type = coin_type
        super().__init__(assets, pos, group)
        self.rect = self.image.get_rect(center = pos)

class Particle(Animated):
    def __init__(self, assets, pos, group):
        super().__init__(assets, pos, group)

    def animate(self, dt):
        self.frame_index += dt * ANIMATION_SPEED
        if self.frame_index < len(self.animation_frames):
            self.image = self.animation_frames[int(self.frame_index)]
        else:
            self.kill()



# Enemies
class Spike(Generic):
    def __init__(self, surf, pos, group):
        super().__init__(pos, surf, group)
        self.rect.midbottom = pos
        self.mask = pygame.mask.from_surface(self.image)
    
class Tooth(Generic):
    def __init__(self, assets, pos, group, collision_sprites):
        self.frame_index = 0
        self.orientation = 'left'
        self.animation_frames = assets
        surf = self.animation_frames[f'run_{self.orientation}'][self.frame_index]
        super().__init__(pos, surf, group)
        self.rect.midbottom = pos
        self.collision_sprites = collision_sprites
        self.mask = pygame.mask.from_surface(self.image)

        # movement
        self.direction = vector(choice((-1, 1)), 0)
        self.orientation = 'left' if self.direction.x < 0 else 'right'
        self.pos = vector(self.rect.topleft)
        self.speed = 150

        if not [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(self.rect.midbottom + vector(0, 10))]:
            self.kill()


    def move(self, dt):
        right_gap = self.rect.bottomright + vector(1, 1)
        right_block = self.rect.midright + vector(1, 0)
        left_gap = self.rect.bottomleft + vector(-1, 1)
        left_block = self.rect.midleft + vector(-1, 0)

        if self.direction.x > 0:
            # no floor collision
            floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(right_gap)]

            # wall collision
            wall_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(right_block)]

            if not floor_sprites or wall_sprites:
                self.direction.x *= -1
                self.orientation = 'left'

        
        if self.direction.x < 0:
            # floor collision
            floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(left_gap)]

            # wall collision
            wall_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.collidepoint(left_block)]

            if not floor_sprites or wall_sprites:
                self.direction.x *= -1
                self.orientation = 'right'


        self.pos += self.speed * dt * self.direction
        self.rect.x = round(self.pos.x)


    def animate(self, dt):
        frames = self.animation_frames[f'run_{self.orientation}']
        self.frame_index += dt * ANIMATION_SPEED
        if self.frame_index >= len(frames):
            self.frame_index = 0
        self.image = frames[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.animate(dt)
        self.move(dt)

class Shell(Generic):
    def __init__(self, orientation, assets, pos, group, pearl_animation, damage_sprites):
        self.status = 'idle'
        self.status = 'attack'
        self.orientation = orientation
        self.frame_index = 0
        self.animation_frames = assets.copy()
        self.cooldown = Stopwatch(200)
        if orientation == 'right':
            for key, value in self.animation_frames.items():
                self.animation_frames[key] = [pygame.transform.flip(frame, True, False) for frame in value]
        super().__init__(pos, self.animation_frames['idle'][self.frame_index], group)
        self.rect.midbottom = pos

        # pearl
        self.pearl_animation = pearl_animation
        self.has_shot = False
        self.damage_sprites = damage_sprites
    
    def get_status(self):
        if vector(self.rect.center).distance_to(self.player.rect.center) < 500 and not self.cooldown.active:
            self.status = 'attack'  
        else:
            self.status = 'idle'
    
    def animate(self, dt):
        self.get_status()
        frames = self.animation_frames[self.status]
        self.frame_index += dt * ANIMATION_SPEED
        if self.frame_index >= len(frames):
            self.frame_index = 0
            if self.has_shot:
                self.cooldown.activate()
                self.has_shot = False
        self.image = frames[int(self.frame_index)]

        if int(self.frame_index) == 2 and self.status == 'attack' and not self.has_shot:
            pearl_direction = vector(-1, 0) if self.orientation == 'left' else vector(1, 0)
            offset = (pearl_direction * 50) + vector(0,-10) if self.orientation == 'left' else (pearl_direction * 20) + vector(0,-10)
            Pearl(self.pearl_animation, pearl_direction, vector(self.rect.center)+ offset, [self.groups()[0], self.damage_sprites])
            self.has_shot = True
    
    def update(self, dt):
        self.animate(dt)
        self.cooldown.update()
        
class Pearl(Generic):
    def __init__(self, assets, direction, pos, group):
        super().__init__(pos, assets, group)

        self.timer = Stopwatch(6000)
        self.pos = vector(self.rect.topleft)
        self.direction = direction 
        self.speed = 100
        self.mask = pygame.mask.from_surface(self.image)


        self.timer.activate()

    def update(self, dt):
        self.pos += self.direction * dt * self.speed
        self.rect.x = round(self.pos.x)

        self.timer.update()

        if not self.timer.active:
            self.kill()



# Player
class Player(Generic):
    def __init__(self, pos, group, collision_sprites, assets, sound):

        self.orientation = 'right'
        self.status = 'idle'
        self.animation_frames = assets
        self.frame_index = 0
        self.sound = sound
        current_animation = self.animation_frames[f'{self.status}_{self.orientation}']
        super().__init__(pos, current_animation[self.frame_index], group)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center = pos)
        self.direction = vector(0,0)
        self.pos = vector(self.rect.center)
        self.speed = 300
        self.on_floor = False
        self.gravity = 4

        # collision
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.inflate(-50, 0)
        self.invul_timer = Stopwatch(200)

    def damage(self):
        if not self.invul_timer.active:
            self.invul_timer.activate()
            self.direction.y -= 1.5
            self.healthbar.health -= 10 if self.healthbar.health > 0 else 0


    def get_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
            self.status = 'run' if self.direction.x != 0 else 'idle'

    def animate(self, dt):
        current_animation = self.animation_frames[f'{self.status}_{self.orientation}']
        self.frame_index += dt * ANIMATION_SPEED
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

        if self.invul_timer.active:
            surf = self.mask.to_surface()
            surf.set_colorkey('black')
            self.image = surf

    
    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.orientation = 'left'
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.orientation = 'right'
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_floor:
            self.direction.y = -2
            self.sound.play_sfx(self.sound.jump)
    
    def move(self, dt):
        self.pos += self.direction * self.speed * dt

        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    self.hitbox.right = sprite.rect.left if self.direction.x > 0 else self.hitbox.right
                    self.hitbox.left = sprite.rect.right if self.direction.x < 0 else self.hitbox.left
                    self.rect.centerx, self.pos.x = self.hitbox.centerx, self.hitbox.centerx
                
                if direction == 'vertical':
                    self.hitbox.bottom = sprite.rect.top if self.direction.y > 0 else self.hitbox.bottom
                    self.hitbox.top = sprite.rect.bottom if self.direction.y < 0 else self.hitbox.top
                    self.rect.centery, self.pos.y = self.hitbox.centery, self.hitbox.centery
                    self.direction.y = 0


    def apply_gravity(self, dt):
        self.direction.y += self.gravity * dt
        self.rect.y += self.direction.y

    def check_on_floor(self):
        self.floor_rect = pygame.Rect(self.hitbox.bottomleft,(self.hitbox.width, 2)) 
        floor_sprites = [sprite for sprite in self.collision_sprites if sprite.rect.colliderect(self.floor_rect)]
        self.on_floor = True if floor_sprites else False

    def update(self, dt):
        self.input()
        self.apply_gravity(dt)
        self.move(dt)
        self.check_on_floor()
        self.invul_timer.update()
        self.get_status()
        self.animate(dt)
