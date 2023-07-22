import pygame, sys 
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_buttons
from pygame.mouse import get_pos as mouse_pos
from settings import *
from imports import *
from menu import Menu
from stopwatch import Stopwatch
from random import choice, randint

class Editor:
	def __init__(self, land_tiles, switch, level):
		# main setup 
		self.display_surface = pygame.display.get_surface()
		self.canvas_data = {}
		self.switch = switch

		

		# imports
		self.land_tiles = land_tiles
		self.imports()

		# navigation
		self.origin = vector()
		self.pan_active = False
		self.pan_offset = vector()

		# support lines 
		self.support_line_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
		self.support_line_surf.set_colorkey('green')
		self.support_line_surf.set_alpha(30)
		
		# clouds
		self.current_clouds = []
		self.cloud_surfs = import_data('../graphics/clouds')
		self.cloud_timer = pygame.USEREVENT + 1
		pygame.time.set_timer(self.cloud_timer, 2000)
		self.startup_clouds()

		# selection
		self.selection_index = 2
		self.last_cell_selected = None

		# objects
		self.canvas_objects = pygame.sprite.Group()
		self.background = pygame.sprite.Group()
		self.foreground = pygame.sprite.Group()
		self.object_drag_active = False
		self.object_timer = Stopwatch(400)

		# menu 
		self.menu = Menu()
		self.level = level

		# Player
		CanvasObject(
			pos = (200, WINDOW_HEIGHT/2),
			object_id=0,
			group = [self.canvas_objects, self.foreground], 
			origin = self.origin, 
			frames = self.animations[0]['frames']
		)

		# Sky
		self.sky_handle = CanvasObject(
			pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2),
			object_id=1,
			group = [self.canvas_objects, self.background], 
			origin = self.origin, 
			frames = [self.handle_surf]
		)

		# End
		CanvasObject(
			pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT),
			object_id=19,
			group = [self.canvas_objects, self.background],
			origin = self.origin,
			frames = [self.end]
		)

	# support
	def get_current_cell(self, pos = None):
		if pos:
			col, row = vector(pos) // TILE_SIZE
		else:
			col, row = (vector(mouse_pos()) - self.origin) // TILE_SIZE
		return int(col), int(row)

	def imports(self):
		self.water_botom = load('../graphics/terrain/water/water_bottom.png').convert_alpha()
		self.start = load('../graphics/terrain/phase/start.png').convert_alpha()
		self.end = load('../graphics/terrain/phase/end.png').convert_alpha()
		self.handle_surf = load('../graphics/cursors/handle.png').convert_alpha()

		# animations
		self.animations = {}
		for key, value in EDITOR_DATA.items():
			if value['graphics']:
				graphics = import_data(value['graphics'])
				self.animations[key] = {
					'index' : 0,
					'frames' : graphics, 
					'length' : len(graphics)
				}
		
		# preview
		self.preview_surfs = {key : load(value['preview']).convert_alpha() for key, value in EDITOR_DATA.items() if value['preview']}

	def check_neighbors(self, cell):
		cluster_size = 3
		cluster = [ (cell[0] + col - 1, cell[1] + row - 1)
	    	for col in range(cluster_size)
		    for row in range(cluster_size)
		] 
		for cell in cluster:
			if cell in self.canvas_data:
				self.canvas_data[cell].terrain_neighbors = []
				for name, side in NEIGHBOR_DIRECTIONS.items():
					neighbor_cell = (cell[0] + side[0], cell[1] + side[1])
					if neighbor_cell in self.canvas_data:
						# terrain
						if self.canvas_data[neighbor_cell].has_terrain:
							self.canvas_data[cell].terrain_neighbors.append(name)
					
						# water
						if self.canvas_data[neighbor_cell].has_water and name == 'A':
							self.canvas_data[cell].has_water_on_top = True

	def mouse_on_object(self):
		for obj in self.canvas_objects:
			if obj.rect.collidepoint(mouse_pos()):
				return obj

	def create_grid(self):
		for cell, tile in self.canvas_data.items():
			tile.objects = []

		for obj in self.canvas_objects:
			current_cell = self.get_current_cell(obj.distance_to_origin)
			offset = obj.distance_to_origin - (vector(current_cell) * TILE_SIZE)
			if current_cell in self.canvas_data:
				self.canvas_data[current_cell].add_id(obj.object_id, offset)
			else:
				self.canvas_data[current_cell] = CanvasTile(obj.object_id, offset)

		layers = {
			'water' : {},
			'terrain' : {},
			'coins' : {},
			'enemies' : {},
			'bg palms' : {},
			'fg objects' : {},
		}
		top = sorted([key for key in self.canvas_data.keys()], key = lambda key: key[1])[0][1] 
		left = sorted([key for key in self.canvas_data.keys()], key = lambda key: key[0])[0][0]

		
		for cell, tile in self.canvas_data.items():

			row_adjusted = cell[1] - top
			col_adjusted = cell[0] - left 
			
			x = col_adjusted * TILE_SIZE
			y = row_adjusted * TILE_SIZE

			if tile.has_water:
				layers['water'][(x, y)] = tile.get_water() 
			
			if tile.has_terrain:
				layers['terrain'][(x, y)] = tile.get_terrain() if tile.get_terrain() in self.land_tiles else 'X'
			
			if tile.coin:
				layers['coins'][(x + TILE_SIZE//2, y + TILE_SIZE//2)] = tile.coin
			
			if tile.enemy:
				layers['enemies'][(x + TILE_SIZE//2, y + TILE_SIZE)] = tile.enemy
			
			for object_id, offset in tile.objects:
				if object_id in [key for key, value in EDITOR_DATA.items() if value['style'] == 'palm_bg']:
					layers['bg palms'][(int(x + offset.x), int(y + offset.y))] = object_id
				else:
					layers['fg objects'][(int(x + offset.x), int(y + offset.y))] = object_id

		return layers
			


	# input
	def event_loop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				self.switch('Levels')
			self.save_level(event)
			self.pan_input(event)
			self.selection_hotkeys(event)
			self.menu_click(event)

			self.object_drag(event)

			self.canvas_add()
			self.canvas_remove()

			self.create_clouds(event)

	def save_level(self, event):
		if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
			save_txt(f'../saves/level{self.level}.txt', self.create_grid())
			
	def pan_input(self, event):

		# middle mouse button pressed / released 
		if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[0]:
			self.pan_active = True
			self.pan_offset = vector(mouse_pos()) - self.origin

		if not mouse_buttons()[0]:
			self.pan_active = False

		# mouse wheel 
		if event.type == pygame.MOUSEWHEEL:
			self.origin.x -= event.x * MOUSE_WHEEL
			self.origin.y += event.y * MOUSE_WHEEL
			for obj in self.canvas_objects:
				obj.pan_pos(self.origin)

		# panning update
		if self.pan_active:
			self.origin = vector(mouse_pos()) - self.pan_offset
			for obj in self.canvas_objects:
				obj.pan_pos(self.origin)

	def selection_hotkeys(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RIGHT:
				self.selection_index += 1
			if event.key == pygame.K_LEFT:
				self.selection_index -= 1
		self.selection_index = max(2,min(self.selection_index, 18))

	def menu_click(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(mouse_pos()):
			button_index = self.menu.click(mouse_pos(), mouse_buttons())
			self.selection_index = button_index if button_index else self.selection_index

	def canvas_add(self):
		if mouse_buttons()[2] and not self.menu.rect.collidepoint(mouse_pos()) and not self.object_drag_active:
			if EDITOR_DATA[self.selection_index]['type'] == 'tile':
				# tile
				current_cell = self.get_current_cell()
				if current_cell != self.last_cell_selected:
					if current_cell in self.canvas_data:
						self.canvas_data[current_cell].add_id(self.selection_index)
					else:
						self.canvas_data[current_cell] = CanvasTile(self.selection_index)
					self.last_cell_selected = current_cell
					self.check_neighbors(current_cell)

			else:
				# object
				if not self.object_timer.active:
					groups = [self.canvas_objects, self.background] if self.selection_index in [key for key, value in EDITOR_DATA.items() if value['style'] == 'palm_bg'] else [self.canvas_objects, self.foreground]
					CanvasObject(
						pos = mouse_pos(),
						object_id=self.selection_index,
						group = groups, 
						origin = self.origin, 
						frames = self.animations[self.selection_index]['frames']
					)
					self.object_timer.activate()

	def canvas_remove(self):
		if pygame.key.get_pressed()[pygame.K_LSHIFT] and mouse_buttons()[2] and not self.menu.rect.collidepoint(mouse_pos()):

			# remove object
			selected_object = self.mouse_on_object()
			if selected_object:
				if EDITOR_DATA[selected_object.object_id]['style'] not in ('player', 'sky', 'phase'):
					selected_object.kill()

			# remove tile
			current_cell = self.get_current_cell()
			if current_cell in self.canvas_data:
				self.canvas_data[current_cell].remove_id(self.selection_index)
				if self.canvas_data[current_cell].is_empty:
					del self.canvas_data[current_cell]
			self.last_cell_selected = current_cell
			self.check_neighbors(current_cell)

	def object_drag(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN and mouse_buttons()[2] :
			for obj in self.canvas_objects:
				if obj.rect.collidepoint(mouse_pos()):
					self.object_drag_active = True
					obj.start_drag()
		
		if event.type == pygame.MOUSEBUTTONUP and self.object_drag_active:
			self.object_drag_active = False
			for obj in self.canvas_objects:
				obj.drag_end(self.origin)


	# drawing 
	def draw_tile_lines(self):
		cols = WINDOW_WIDTH // TILE_SIZE
		rows = WINDOW_HEIGHT// TILE_SIZE

		origin_offset = vector(
			x = self.origin.x - int(self.origin.x / TILE_SIZE) * TILE_SIZE,
			y = self.origin.y - int(self.origin.y / TILE_SIZE) * TILE_SIZE)

		self.support_line_surf.fill('green')

		for col in range(cols + 1):
			x = origin_offset.x + col * TILE_SIZE
			pygame.draw.line(self.support_line_surf,LINE_COLOR, (x,0), (x,WINDOW_HEIGHT))

		for row in range(rows + 1):
			y = origin_offset.y + row * TILE_SIZE
			pygame.draw.line(self.support_line_surf,LINE_COLOR, (0,y), (WINDOW_WIDTH,y))

		self.display_surface.blit(self.support_line_surf,(0,0))

	def draw_level(self):
		self.background.draw(self.display_surface)
		for cell, tile in self.canvas_data.items():
			cell_pos = self.origin + vector(cell)*TILE_SIZE

			if tile.has_water:
				if tile.has_water_on_top:
					surf = self.water_botom
				else:
					frame_index = int(self.animations[3]['index'])
					surf = self.animations[3]['frames'][frame_index]
				self.display_surface.blit(surf, cell_pos)
			

			if tile.has_terrain:
				tile_string = ''.join(tile.terrain_neighbors)
				tile_name = tile_string if tile_string in self.land_tiles else 'X'
				surf = self.land_tiles[tile_name]
				self.display_surface.blit(surf, cell_pos)
			
			
			if tile.coin:
				frame_index = int(self.animations[tile.coin]['index'])
				surf = self.animations[tile.coin]['frames'][frame_index]
				rect = surf.get_rect(center= (cell_pos.x + TILE_SIZE/2, cell_pos.y+ TILE_SIZE/2))
				self.display_surface.blit(surf, rect)

			
			if tile.enemy:
				frame_index = int(self.animations[tile.enemy]['index'])
				surf = self.animations[tile.enemy]['frames'][frame_index]
				rect = surf.get_rect(midbottom= (cell_pos.x + TILE_SIZE/2, cell_pos.y+ TILE_SIZE))
				self.display_surface.blit(surf, rect)

		self.foreground.draw(self.display_surface)		

	def preview(self):
		selected_object = self.mouse_on_object()
		if not self.menu.rect.collidepoint(mouse_pos()):
			if selected_object:
				rect = selected_object.rect.inflate(10,10)
				color = 'black'
				size = 15
				width = 3

				# topleft
				pygame.draw.lines(self.display_surface, color, False, ((rect.left, rect.top + size), (rect.left, rect.top), (rect.left + size, rect.top)), width)
				# topright
				pygame.draw.lines(self.display_surface, color, False, ((rect.right - size, rect.top), (rect.right, rect.top), (rect.right, rect.top + size)), width)
				# bottomleft
				pygame.draw.lines(self.display_surface, color, False, ((rect.left, rect.bottom - size), (rect.left, rect.bottom), (rect.left + size, rect.bottom)), width)
				# bottomright
				pygame.draw.lines(self.display_surface, color, False, ((rect.right - size, rect.bottom), (rect.right, rect.bottom), (rect.right, rect.bottom - size)), width)

			else:
				type_dict = {key : value['type'] for key, value in EDITOR_DATA.items()}
				surf = self.preview_surfs[self.selection_index].copy()
				surf.set_alpha(200)

				# tile
				current_cell = self.get_current_cell()
				if type_dict[self.selection_index] == 'tile':
					rect = surf.get_rect(midbottom= (current_cell[0]*TILE_SIZE+ self.origin.x + TILE_SIZE/2 , current_cell[1]*TILE_SIZE+ self.origin.y + TILE_SIZE))
				else:
					rect = surf.get_rect(center= mouse_pos())

				self.display_surface.blit(surf, rect)

	def display_sky(self, dt):	

		self.display_surface.fill(SKY_COLOR)
		y = self.sky_handle.rect.centery

		
		# horizon lines
		if y > 0:
			horizon_rect1 = pygame.Rect(0, y-10, WINDOW_WIDTH,  10)
			horizon_rect2 = pygame.Rect(0, y-16, WINDOW_WIDTH, 4)
			horizon_rect3 = pygame.Rect(0, y-20, WINDOW_WIDTH, 2)
			pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect1)
			pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect2)
			pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect3)

			self.display_clouds(dt, y)

		# sea
		if 0 < y < WINDOW_HEIGHT:
			sea_rect = pygame.Rect(0, y, WINDOW_WIDTH, WINDOW_HEIGHT)
			pygame.draw.rect(self.display_surface, SEA_COLOR, sea_rect)
		if y <= 0:
			self.display_surface.fill(SEA_COLOR)

		pygame.draw.line(self.display_surface, HORIZON_COLOR, (0, y), (WINDOW_WIDTH, y), 3)

	def create_clouds(self, event):
		if event.type == self.cloud_timer:
			surf = choice(self.cloud_surfs)
			surf = pygame.transform.scale2x(surf) if randint(0,4) < 2 else surf
			pos = [WINDOW_WIDTH + randint(0, 100), randint(0, WINDOW_HEIGHT)]
			self.current_clouds.append({'surf' : surf, 'pos' : pos, 'speed' : randint(20,50)})
		
			# remove clouds
			self.current_clouds = [cloud for cloud in self.current_clouds if cloud['pos'][0] > -400]

	def display_clouds(self, dt, horizon_y):
		for cloud in self.current_clouds:
			cloud['pos'][0] -= cloud['speed'] * dt
			x = cloud['pos'][0]
			y = horizon_y - cloud['pos'][1] 
			self.display_surface.blit(cloud['surf'], (x, y))
		
	def startup_clouds(self):
		for i in range(20):
			surf = pygame.transform.scale2x(choice(self.cloud_surfs)) if randint(0,4) < 2 else choice(self.cloud_surfs)
			self.current_clouds.append({
				'surf' : surf, 
				'pos' : [randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)], 
				'speed' : randint(20,50)
			})
		

	# update
	def run(self, dt):
		self.event_loop()

		# drawing
		self.display_surface.fill('gray')
		self.display_sky(dt)
		self.draw_tile_lines()
		pygame.draw.circle(self.display_surface, 'red', self.origin, 10)
		self.draw_level()
		self.preview()
		self.menu.display(self.selection_index)

		# update
		self.animation_update(dt)
		self.canvas_objects.update(dt)
		self.object_timer.update()

	def animation_update(self, dt):
		for key in self.animations.keys():
			self.animations[key]['index'] += dt * ANIMATION_SPEED
			if self.animations[key]['index'] >= self.animations[key]['length']:
				self.animations[key]['index'] = 0
		


class CanvasTile:
	def __init__(self, tile_id, offset = vector()):

		# terrain
		self.has_terrain = False
		self.terrain_neighbors = []

		# water
		self.has_water = False
		self.has_water_on_top = False

		# coin 
		self.coin = None

		# enemy
		self.enemy = None

		# objects
		self.objects = []

		self.add_id(tile_id, offset)
		self.is_empty = False
	
	def add_id(self, tile_id, offset = vector()):
		options = {key : value['style'] for key, value in EDITOR_DATA.items()}
		match options[tile_id]:
			case 'terrain': self.has_terrain = True
			case 'water': self.has_water = True
			case 'coin' : self.coin = tile_id
			case 'enemy' : self.enemy = tile_id
			case _ : 
				if (tile_id, offset) not in self.objects:
					self.objects.append((tile_id, offset))

	def remove_id(self, tile_id):
		options = {key : value['style'] for key, value in EDITOR_DATA.items()}
		match options[tile_id]:
			case 'terrain': self.has_terrain = False
			case 'water': self.has_water = False
			case 'coin' : self.coin = None
			case 'enemy' : self.enemy = None

		self.check_content()

	def check_content(self):
		if not self.has_terrain and not self.has_water and self.coin == None and self.enemy == None:
			self.is_empty == True

	def get_water(self):
		return 'bottom' if self.has_water_on_top else 'top'

	def get_terrain(self):
		return ''.join(self.terrain_neighbors)

class CanvasObject(pygame.sprite.Sprite):
	def __init__(self, pos, object_id, group, origin, frames):
		super().__init__(group)

		# rect
		self.image = frames[0]
		self.rect = self.image.get_rect(center = pos)
		self.distance_to_origin = vector(self.rect.topleft) - origin
		self.object_id = object_id

		# drag
		self.drag_active = False
		self.mouse_offset = vector()

		# animation
		self.frames = frames
		self.frame_index = 0
	
	def start_drag(self):
		self.drag_active = True
		self.mouse_offset = vector(mouse_pos()) - self.rect.topleft

	def drag(self):
		if self.drag_active:
			self.rect.topleft = vector(mouse_pos()) - self.mouse_offset

	def drag_end(self, origin):
		self.drag_active = False
		self.distance_to_origin = self.rect.topleft - origin
	
	def pan_pos(self, origin):
		self.rect.topleft = origin + self.distance_to_origin

	def animation_update(self, dt):
		self.frame_index += dt * ANIMATION_SPEED
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		index = int(self.frame_index)
		self.image = self.frames[index]
		self.rect = self.image.get_rect(midbottom = self.rect.midbottom)

	def update(self, dt):
		self.drag()
		self.animation_update(dt)





