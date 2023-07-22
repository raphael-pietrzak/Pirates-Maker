import pygame, sys
from sprites import Generic, Player, Animated, Coin, Particle, Spike, Tooth, Shell, Block, Cloud
from ui import Wallet, HealthBar
from settings import *
from stopwatch import Timer
from pygame import Vector2 as vector
from random import choice, randint
from pygame.image import load




class Level:
    def __init__(self, grid, switch, asset_dict, sound, level_id):
        self.display_surface = pygame.display.get_surface()
        self.switch = switch

        self.all_sprites = CameraGroup()
        self.coin_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.shell_sprites = pygame.sprite.Group()
        self.ui_sprites = pygame.sprite.Group()


        self.timer = Timer()
        self.level_id = level_id


        # audio
        self.sound = sound
        self.sound.play_music(self.sound.super_hero)


        self.build_level(grid, asset_dict)
        self.coin_surf = load('../graphics/ui/coin.png')
        self.wallet = Wallet((50, 80), self.coin_surf, self.ui_sprites)
        self.health_bar_surf = load('../graphics/ui/health_bar.png')
        self.player.healthbar = HealthBar((50, 20), self.health_bar_surf, self.ui_sprites)



        # particles
        self.particle_surfs = asset_dict['particle']

        # clouds
        right_max_pos = sorted(list(grid['terrain'].keys()), key=lambda pos: pos[0])[-1][0] if grid['terrain'] else WINDOW_WIDTH + 500
        self.clouds_limit = {
            'left': -WINDOW_WIDTH,
            'right': right_max_pos
        }
        self.cloud_surfs = asset_dict['clouds']
        self.cloud_timer = pygame.USEREVENT + 2
        pygame.time.set_timer(self.cloud_timer, 2000)
        self.startup_clouds()
        
    
    # input
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.sound.play_music(self.sound.explorer)
                self.switch('Levels')
            self.create_clouds(event)

    def create_clouds(self, event):
        if event.type == self.cloud_timer:
            surf = choice(self.cloud_surfs)
            surf = pygame.transform.scale2x(surf) if randint(0,4) < 2 else surf
            x = self.clouds_limit['right'] + randint(600, 800)
            y = self.horizon_y  - randint( 50, 600 )
            Cloud((x, y), surf, self.all_sprites, self.clouds_limit['left'])

    def startup_clouds(self):
        clouds_number = int((self.clouds_limit['right'] - self.clouds_limit['left']) / 80)

        for _ in range(clouds_number):
            surf = pygame.transform.scale2x(choice(self.cloud_surfs)) if randint(0,4) < 2 else choice(self.cloud_surfs)
            x = randint(self.clouds_limit['left'], self.clouds_limit['right'] + 500)
            y = self.horizon_y  - randint( 50, 600 )
            Cloud((x, y), surf, self.all_sprites, self.clouds_limit['left'])
    
    
    # build
    def build_level(self, grid, asset_dict):
        for layer_name, layer in grid.items():
            for pos, data in layer.items():
                if layer_name == 'terrain': # case 2
                    Generic(pos, asset_dict['land'][data], [self.all_sprites, self.collision_sprites])
                if layer_name == 'water':   # case 3
                    if data == 'top':
                        Animated(asset_dict['water top'],pos, self.all_sprites, LEVEL_LAYERS['water'])
                    else:
                        Generic(pos, asset_dict['water bottom'], self.all_sprites, LEVEL_LAYERS['water'])
                
                match data:
                    case 0: self.player = Player(pos, self.all_sprites, self.collision_sprites, asset_dict['player'], self.sound)

                    case 1:
                        self.horizon_y = pos[1]
                        self.all_sprites.horizon_y = self.horizon_y
                    # coins
                    case 4: Coin('gold', asset_dict['gold'], pos, [self.all_sprites, self.coin_sprites])
                    case 5: Coin('silver', asset_dict['silver'], pos, [self.all_sprites, self.coin_sprites])
                    case 6: Coin('diamond', asset_dict['diamond'], pos, [self.all_sprites, self.coin_sprites])

                    # enemies
                    case 7: Spike(asset_dict['spikes'], pos, [self.all_sprites, self.damage_sprites])
                    case 8: Tooth(asset_dict['tooth'], pos, [self.all_sprites, self.damage_sprites], self.collision_sprites)
                    case 9: 
                        Shell(
                            orientation='left', 
                            assets=asset_dict['shell'], 
                            pos=pos, 
                            group=[self.all_sprites, self.collision_sprites, self.shell_sprites], 
                            pearl_animation=asset_dict['pearl'],
                            damage_sprites=self.damage_sprites)
                        Block(pos, (80, 50), self.collision_sprites)
                    case 10: 
                        Shell(
                            orientation='right', 
                            assets=asset_dict['shell'], 
                            pos=pos, 
                            group=[self.all_sprites,self.collision_sprites, self.shell_sprites],
                            pearl_animation=asset_dict['pearl'],
                            damage_sprites=self.damage_sprites)
                        Block(pos, (80, 50), self.collision_sprites)

                    # palm trees
                    case 11: 
                        Animated(asset_dict['palm']['small_fg'], pos, self.all_sprites)
                        Block(pos, (80, 50), self.collision_sprites)
                    case 12: 
                        Animated(asset_dict['palm']['large_fg'], pos, self.all_sprites)
                        Block(pos, (80, 50), self.collision_sprites)
                    case 13: 
                        Animated(asset_dict['palm']['left_fg'], pos, self.all_sprites)
                        Block(pos, (80, 50), self.collision_sprites)
                    case 14: 
                        Animated(asset_dict['palm']['right_fg'], pos, self.all_sprites)
                        Block(pos + vector(50, 0), (80, 50), self.collision_sprites)

                    case 15: Animated(asset_dict['palm']['small_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                    case 16: Animated(asset_dict['palm']['large_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                    case 17: Animated(asset_dict['palm']['left_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])
                    case 18: Animated(asset_dict['palm']['right_bg'], pos, self.all_sprites, LEVEL_LAYERS['bg'])

                    case 19: self.end = Generic(pos, asset_dict['end'], [self.all_sprites])
                    
                    case _:
                        pass

        try : self.end 
        except : self.end = Generic((0, 0), asset_dict['end'], [self.all_sprites])
        
        for sprite in self.shell_sprites:
            sprite.player = self.player

    def get_coins(self):
        collided_coins = pygame.sprite.spritecollide(self.player, self.coin_sprites, True)
        for sprite in collided_coins:
            Particle(self.particle_surfs, sprite.rect.center, self.all_sprites)
            self.wallet.coins += 1
            self.sound.play_sfx(self.sound.coin)

    def get_damage(self):
        damage_sprites = pygame.sprite.spritecollide(self.player, self.damage_sprites, False, pygame.sprite.collide_mask)
        if damage_sprites:
            self.player.damage()
            self.sound.play_sfx(self.sound.hit)
        

    def get_finish(self):
        self.duration = self.timer.get_time()
        if self.player.rect.y > self.horizon_y + WINDOW_HEIGHT or self.player.healthbar.health <= 0:
            self.switch('End', self.level_id, self.duration, 'Game Over')
        if self.end.rect.colliderect(self.player.rect):
            self.switch('End', self.level_id, self.duration, 'Victory')


    # update
    def run(self, dt):
        self.event_loop()
        self.all_sprites.update(dt)
        self.ui_sprites.update(dt)
        self.get_coins()
        self.get_damage()
        self.get_finish()
        self.display_surface.fill(SKY_COLOR)
        self.all_sprites.custom_draw(self.player)
        self.ui_sprites.draw(self.display_surface)
        self.ui_sprites.update(dt)
        

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector(0, 0)

    def draw_horizon(self):
        horizon_pos = self.horizon_y - self.offset.y

		
		# horizon lines
        if horizon_pos > 0:
            horizon_rect1 = pygame.Rect(0, horizon_pos-10, WINDOW_WIDTH,  10)
            horizon_rect2 = pygame.Rect(0, horizon_pos-16, WINDOW_WIDTH, 4)
            horizon_rect3 = pygame.Rect(0, horizon_pos-20, WINDOW_WIDTH, 2)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect1)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect2)
            pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect3)

		# sea
        if 0 < horizon_pos < WINDOW_HEIGHT:
            sea_rect = pygame.Rect(0, horizon_pos, WINDOW_WIDTH, WINDOW_HEIGHT)
            pygame.draw.rect(self.display_surface, SEA_COLOR, sea_rect)
        if horizon_pos <= 0:
            self.display_surface.fill(SEA_COLOR)

        pygame.draw.line(self.display_surface, HORIZON_COLOR, (0, horizon_pos), (WINDOW_WIDTH, horizon_pos), 3)

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - WINDOW_WIDTH/2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT/2


        for sprite in self:
            if sprite.z == LEVEL_LAYERS['clouds']:
                offset_rect = sprite.rect.copy()
                offset_rect.center -= self.offset
                self.display_surface.blit(sprite.image, offset_rect)

        self.draw_horizon()

        for layer in LEVEL_LAYERS.values():
            for sprite in self:
                if sprite.z == layer and sprite.z != LEVEL_LAYERS['clouds']:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)