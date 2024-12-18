# https://www.desmos.com/calculator/2o5u3ueaqb

import math
from PIL import Image
import numpy as np
from typing import List, Literal, Optional

class ContinuousRange:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __contains__(self, value):
        return self.start <= value <= self.stop

class Camera:
	x:float
	y:float

	def __init__(self,x=None,y=None,theta=None) -> None:
		if theta is None: 
			theta = math.pi/4
		if x is None:
			x = 0
		if y is None:
			y = 0

		self.x = x
		self.y = y
		self.theta = theta
		self.m = math.tan(0.5 * theta)

class Screen:
	def __init__(self) -> None:
		# Doesn't work with height other than 1 
		# defined as being at the same position as the "backwall". objects past this appear smaller than "true size"
		self.height:float = 1
		self.y:float = 0
		self.top:float = self.y + 0.5 * self.height
		self.bottom:float = self.y - 0.5 * self.height

class Block:
	def __init__(self,x,y,height) -> None:
		self.x:float = x
		self.y:float = y
		self.height:float = height
		self.top:float = self.y + 0.5*self.height
		self.bottom:float = self.y - 0.5*self.height

class Renderer:
	def __init__(self, blocks:Optional[List[Block]]=None) -> None:
		self.camera = Camera()
		self.screen = Screen()
		self.blocks:List[Block] = [] if blocks is None else blocks
		self.BACK_WALL_X = 2

	def get_rendered_block(self,block:Block):
		scale_factor = self.BACK_WALL_X / block.x # (y_{bw} = m x_{bw}) / (y_b = m x_b) and so the Ms cancel
		new_y = scale_factor*block.y
		new_height = scale_factor*block.height
		new_block = Block(0, new_y, new_height) # the x doesn't matter
		return new_block

	def trim_out_of_view(self, block:Block):
		block.top = min(block.top, self.camera.m * self.BACK_WALL_X) # y = mx
		block.bottom = max(block.bottom, -self.camera.m * self.BACK_WALL_X ) # y = -mx

	def normalize(self, placed_object:Screen|Block):
		#TODO: before adding 0.5, we need to make sure it's actually -1 to 1, since rn it's -mx to mx.
		# divide both sides by mx
		normalizing_scale = 1/self.camera.m * self.BACK_WALL_X
		placed_object.y *= normalizing_scale
		placed_object.top *= normalizing_scale
		placed_object.bottom *= normalizing_scale
		placed_object.y += 0.5
		placed_object.top += 0.5
		placed_object.bottom += 0.5
	
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
		Projects the block onto the quantized screen
		'''
		topmost_partition_index = self.find_projected_partition(block.top, ranges)
		bottommost_partition_index = self.find_projected_partition(block.bottom, ranges)
		active_partitions = list(range(topmost_partition_index, bottommost_partition_index+1))
		return active_partitions
	
	def create_vector_from_partitions(self, active_partition_indices:list[int], resolution:int) -> np.typing.NDArray[np.float64]:
		vector = np.zeros(resolution, dtype=int)
		vector[active_partition_indices] = 1
		return vector

	def generate_position_vector(self, block:Block, resolution:int):
		RESOLUTION = 10
		rendered_block = self.get_rendered_block(block)
		self.trim_out_of_view(rendered_block)
		self.normalize(block)
		self.normalize(self.screen)
		ranges = self.quantize(RESOLUTION)
		active_partitions = self.project_onto_screen(ranges, block)
		vector = self.create_vector_from_partitions(active_partitions, RESOLUTION)
		return vector

	def generate_all_position_vectors(self, resolution) -> List[np.ndarray]:
		all_vectors = []
		for block in self.blocks:
			vector = self.generate_position_vector(block, resolution)
			all_vectors.append(vector)
		return all_vectors

	def combine_vectors(self, vectors:List[np.ndarray], resolution) -> np.ndarray|Literal[0]:
		#TODO: include colour or at least brightness information here somehow
		if not vectors:
			return np.zeros(resolution, dtype=int)
		return sum(vectors)

	def generate_image(self, rendered_vector:np.ndarray):
		WIDTH = 100
		HEIGHT = 500
		old_width = 1
		old_height = rendered_vector.shape[0]
		initial_image = Image.new(mode="RGB",size=(old_width, old_height))
		horizontally_scaled_image = initial_image.resize((WIDTH, 1), resample=Image.Resampling.NEAREST)
		final_image = horizontally_scaled_image.resize((WIDTH, HEIGHT), resample=Image.Resampling.NEAREST)
		final_image.show()
		

	def render(self, resolution:int):
		#TODO: make the user able to pick final image resolution, not the vector size. that should be default of, say, 100.
		vectors = self.generate_all_position_vectors(resolution)
		rendered_form = self.combine_vectors(vectors, resolution)
		if not rendered_form:
			return np.zeros(resolution, dtype=int)
		self.generate_image(rendered_form)