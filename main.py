# https://www.desmos.com/calculator/2o5u3ueaqb

import math
from PIL import Image
import numpy as np
from typing import List, Literal, Optional
from mpmath import mp, tan, atan

mp.dps = 50  


class ContinuousRange:
	def __init__(self, start, stop):
		if start > stop:
			raise ValueError("start must be less than or equal to stop")
		self.start = start
		self.stop = stop


	def __contains__(self, value):
		return self.start <= value <= self.stop

class Camera:
	x:float
	y:float

	def __init__(self,x=None,y=None,theta=None,forced_screen_height=None) -> None:
		if (theta is None) and (not forced_screen_height is None): 
			theta = 2*atan(forced_screen_height/4)
		elif (not theta is None) and (forced_screen_height is None):
			theta = theta
		elif theta is None and forced_screen_height is None:
			theta = math.pi/4
		else:
			raise ValueError("Theta and forced_screen_height can't both be set")
		
		if x is None:
			x = 0
		if y is None:
			y = 0

		self.x = x
		self.y = y
		self.theta = theta
		self.m = tan(0.5 * theta)

class Screen:
	def __init__(self) -> None:
		# Doesn't work with height other than 1 
		# defined as being at the same position as the "backwall". objects past this appear smaller than "true size"
		self.height:float = 1
		self.y:float = 0
		self.top:float = self.y + 0.5 * self.height
		self.bottom:float = self.y - 0.5 * self.height


class ProjectionScreen:
	def __init__(self, camera:Camera) -> None:
		self.x = 2
		self.y = 0
		self.top = camera.m * self.x # intersection of screen.x and y = mx
		self.bottom = -camera.m * self.x # y = -mx
		self.height = 2 * camera.m * self.x 

class Block:
	def __init__(self,x,y,height) -> None:
		self.x:float = x
		self.y:float = y
		self.height:float = height
		self.top:float = self.y + 0.5*self.height
		self.bottom:float = self.y - 0.5*self.height

class Renderer:
	def __init__(self, blocks:Optional[List[Block]]=None, camera:Optional[Camera]=None) -> None:
		self.camera = Camera() if camera is None else camera
		self.screen = Screen()
		self.blocks:List[Block] = [] if blocks is None else blocks
		self.projected_screen = ProjectionScreen(self.camera)

	def get_rendered_block(self,block:Block):
		scale_factor = self.projected_screen.x / block.x # (y_p = m x_p) / (y_b = m x_b) and so the Ms cancel
		new_y = scale_factor*block.y
		new_height = scale_factor*block.height
		new_block = Block(0, new_y, new_height) # the x doesn't matter
		return new_block

	def trim_out_of_view(self, block:Block):
		block.top = min(block.top, self.projected_screen.top)
		block.bottom = max(block.bottom, self.projected_screen.bottom)

	def normalize(self, placed_object:Screen|Block):
		#TODO: before adding 0.5, we need to make sure it's actually -1 to 1, so we scale everything down to the size of the projected screen
		self.scale_to_one(placed_object)
		self.y_translate(placed_object, 0.5)

	def scale_to_one(self, placed_object):
		placed_object.y /= self.projected_screen.height
		placed_object.top /= self.projected_screen.height
		placed_object.bottom /= self.projected_screen.height
		placed_object.height /= self.projected_screen.height

	def y_translate(self, placed_object, amount):
		placed_object.y += amount
		placed_object.top += amount
		placed_object.bottom += amount

	
	def quantize(self, resolution=5) -> List[ContinuousRange]:
		'''
		`resolution`: number of slices to cut the slider (screen) into.
					 Higher number results in a less pixelated render

		returns a list of ranges (slices). 
		example with 5 partitions:
			(0,0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8,1.0)
		'''
		ranges = []
		range_size = 1/resolution # e.g, 0.2
		for i in range(resolution):
			new_range_start = i * range_size # for example 0*0.2, 1*0.2, etc
			new_range_end = new_range_start + range_size
			ranges.append(ContinuousRange(new_range_start, new_range_end))
		return ranges

	def find_projected_partition(self, y_position, partitions) -> int:
		for i, partition in enumerate(partitions):
			if y_position in partition:
				return i
		raise ValueError("Object is outside the screen and could not be mapped")

	def project_onto_screen(self, ranges:List[ContinuousRange], block:Block) -> List[int]:
		'''
		Projects the block onto the quantized screen by returning all the partitions that have a value
		'''
		topmost_partition_index = self.find_projected_partition(block.top, ranges)
		bottommost_partition_index = self.find_projected_partition(block.bottom, ranges)
		active_partitions = list(range(bottommost_partition_index, topmost_partition_index+1))
		return active_partitions
	
	def create_vector_from_partitions(self, active_partition_indices:list[int], resolution:int) -> np.typing.NDArray[np.float64]:
		vector = np.zeros(resolution, dtype=int)
		vector[active_partition_indices] = 1
		return vector

	def generate_position_vector(self, block:Block, resolution:Optional[int]=None):
		resolution = 5 if resolution is None else resolution
		rendered_block = self.get_rendered_block(block)
		self.trim_out_of_view(rendered_block)
		self.normalize(rendered_block)
		# self.normalize(self.screen) unnecessary since the quantise step doesn't use the screen for the ranges, it just makes a new one
		ranges = self.quantize(resolution)
		active_partitions = self.project_onto_screen(ranges, rendered_block)
		vector = self.create_vector_from_partitions(active_partitions, resolution)
		return vector

	def generate_all_position_vectors(self, resolution) -> List[np.ndarray]:
		all_vectors = []
		for block in self.blocks:
			vector = self.generate_position_vector(block, resolution)
			all_vectors.append(vector)
		return all_vectors

	def combine_vectors(self, vectors:List[np.ndarray], resolution) -> np.ndarray:
		#TODO: include colour or at least brightness information here somehow
		result_vector = sum(vectors, np.zeros_like(vectors[0]))
		return result_vector

	def generate_image(self, rendered_vector:np.ndarray):
		WIDTH = 100
		HEIGHT = 500
		BG_COLOR = (255,255,255)
		OBJECT_COLOR = (0,0,0)
		old_width = 1
		old_height = rendered_vector.shape[0]
		initial_image = Image.new(mode="RGB",size=(old_width, old_height))
		color_map = [BG_COLOR if val == 0 else OBJECT_COLOR for val in rendered_vector[::-1]]
		initial_image.putdata(color_map)
		horizontally_scaled_image = initial_image.resize((WIDTH, old_height), resample=Image.Resampling.NEAREST)
		final_image = horizontally_scaled_image.resize((WIDTH, HEIGHT), resample=Image.Resampling.NEAREST)
		final_image.show(title="final")
		

	def render(self, resolution:int):
		#TODO: make the user able to pick final image resolution, not the vector size. that should be default of, say, 100.
		vectors = self.generate_all_position_vectors(resolution)
		rendered_form = self.combine_vectors(vectors, resolution)
		self.generate_image(rendered_form)



def test_render():
	blocks = [
		Block(2,0.4,0.96)
	]
	renderer = Renderer(blocks=blocks, camera=Camera(forced_screen_height=1))
	renderer.render(500)
test_render()