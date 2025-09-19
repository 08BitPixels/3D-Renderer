import pygame
from math import atan, degrees
from time import time

pygame.init()

class Window:

	def __init__(self, dimensions: tuple[int, int], fps: int) -> None:
		
		self._DIMENSIONS = dimensions
		self._FPS = fps
		self._SURF = pygame.display.set_mode(self._DIMENSIONS)
		self._CLOCK = pygame.time.Clock()

		pygame.display.set_caption(title = '3D Renderer')
		
		self._prev_time = time()
		self._dt = 1.0

	def update(self) -> None:
		
		pygame.display.update()
		self.clock.tick(self.fps)
		
		self._dt = time() - self._prev_time
		self._prev_time = time()
		
	def to_pygame_coords(self, coords: tuple[float, float] | pygame.math.Vector2) -> pygame.math.Vector2:
		
		x = coords[0] + (self.width / 2)
		y = -(coords[1] - (self.height / 2))
		
		return pygame.math.Vector2((x, y))

	# PROPERTIES
	
	@ property
	def dt(self) -> float:
		return self._dt

	@ property
	def dimensions(self) -> tuple[int, int]:
		return self._DIMENSIONS

	@ property
	def width(self) -> int:
		return self._DIMENSIONS[0]

	@ property
	def height(self) -> int:
		return self._DIMENSIONS[1]
		
	@ property
	def surf(self) -> pygame.Surface:
		return self._SURF
	
	@ property
	def clock(self) -> pygame.time.Clock:
		return self._CLOCK
	
	@ property
	def fps(self) -> int:
		return self._FPS

class ViewPoint:
	
	def __init__(self, window: Window, pos: tuple[int, int, int], fov: float) -> None:

		self._WINDOW = window
		self._MOVESPEED = 100
		self._ZOOMSPEED = 100
	
		self._pos = pygame.Vector3(pos)
		self._fov = fov

	def update(self) -> None:

		def input() -> None:

			keys_pressed = pygame.key.get_pressed()
			
			self._pos.x += (keys_pressed[pygame.K_d] - keys_pressed[pygame.K_a]) * self._MOVESPEED * self._WINDOW.dt
			self._pos.y += (keys_pressed[pygame.K_SPACE] - keys_pressed[pygame.K_LSHIFT]) * self._MOVESPEED * self._WINDOW.dt
			self._pos.z += (keys_pressed[pygame.K_w] - keys_pressed[pygame.K_s]) * self._MOVESPEED * self._WINDOW.dt

		input()

	def adj_fov(self, scrollwheel: int) -> None:
		
		self._fov -= self._ZOOMSPEED * scrollwheel * self._WINDOW.dt
		if self._fov < 1: self._fov = 1
		if self._fov > 180: self._fov = 180

	# PROPERTIES

	@ property
	def fov(self) -> float:
		return self._fov

	@ property
	def pos(self) -> pygame.math.Vector3:
		return self._pos

class Polygon:
	
	def __init__(self, vertices: list[pygame.math.Vector3], anchor: int) -> None:
		
		self._vertices = vertices
		self._pos = vertices[anchor]
	
	# PROPERTIES

	@ property
	def vertices(self) -> list[pygame.math.Vector3]:
		return self._vertices
		
	@ property
	def pos(self) -> pygame.math.Vector3:
		return self._pos

class Cube(Polygon):

	def __init__(self, anchor: int, pos: tuple[int, int, int], side_length: int) -> None:

		self._side_length = side_length
		self._pos = pygame.math.Vector3(pos)

		vertices = list(
			map(
				pygame.math.Vector3, 
				[
					(self.pos.x, self.pos.y, self.pos.z),
					(self.pos.x, self.pos.y, self.pos.z + side_length),
					(self.pos.x, self.pos.y + side_length, self.pos.z),
					(self.pos.x, self.pos.y + side_length, self.pos.z + side_length),
					(self.pos.x + side_length, self.pos.y, self.pos.z),
					(self.pos.x + side_length, self.pos.y, self.pos.z + side_length),
					(self.pos.x + side_length, self.pos.y + side_length, self.pos.z),
					(self.pos.x + side_length, self.pos.y + side_length, self.pos.z + side_length),
				]
			)
		)

		super().__init__(vertices = vertices, anchor = anchor)

class RenderEngine:
	
	def __init__(self, window: Window) -> None:
		
		self._WINDOW = window
	
	def render(self, polygons: list[Polygon], viewpoint: ViewPoint) -> None:

		coords = []
	
		for polygon in polygons:

			for vertice in polygon.vertices:
			
				x_diff = vertice.x - viewpoint.pos.x
				y_diff = vertice.y - viewpoint.pos.y
				z_diff = vertice.z - viewpoint.pos.z
				
				x_angle = degrees(atan(x_diff / z_diff))
				y_angle = degrees(atan(y_diff / z_diff))
				
				fov = viewpoint.fov / 2
				x = (x_angle / fov) * (self._WINDOW.width / 2)
				y = (y_angle / fov) * (self._WINDOW.height / 2) 
				coords.append(self._WINDOW.to_pygame_coords((x, y)))
				
				for i in range(len(coords) - 1):
					pygame.draw.line(self._WINDOW.surf, '#000000', coords[i], coords[i + 1], width = 2)

def main() -> None:
	
	font = pygame.font.Font('fonts/pixel_font.ttf', size = 25)
	window = Window(
		dimensions = (1000, 1000),
		fps = 144
	)
	render_engine = RenderEngine(
		window = window
	)
	viewpoint = ViewPoint(
		window = window, 
		pos = (-10, 0, -10), 
		fov = 90
	)

	cubes: list[Polygon] = [Cube(anchor = 0, pos = (0, 0, 0), side_length = 10)]
			
	while True:
	
		for event in pygame.event.get():
		
			if event.type == pygame.QUIT:

				pygame.quit()
				exit()

			if event.type == pygame.MOUSEWHEEL:
				viewpoint.adj_fov(scrollwheel = event.y)
	
		window.surf.fill('#ffffff')

		text1_surf = font.render(f'FOV {round(viewpoint.fov)} deg.', False, '#000000')
		text1_rect = text1_surf.get_rect(topleft = (0, 0))

		text2_surf = font.render(f'POS {[round(x, 2) for x in viewpoint.pos]}', False, '#000000')
		text2_rect = text2_surf.get_rect(topleft = (0, 25))
		
		text3_surf = font.render(f'FPS {round(window.clock.get_fps(), 2)}', False, '#000000')
		text3_rect = text3_surf.get_rect(topleft = (0, 50))

		window.surf.blit(text1_surf, text1_rect)
		window.surf.blit(text2_surf, text2_rect)
		window.surf.blit(text3_surf, text3_rect)
		
		viewpoint.update()
		render_engine.render(polygons = cubes, viewpoint = viewpoint)
		
		window.update()
	
if __name__ == '__main__': main()