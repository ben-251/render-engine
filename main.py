import math
from typing import List

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
	def __init__(self) -> None:
		self.camera = Camera()
		self.screen = Screen()
		self.blocks:List[Block] = []
		self.BACK_WALL = 2

	def get_rendered_block(self,block:Block):
		scale_factor = self.BACK_WALL / block.x # (y_{bw} = m x_{bw}) / (y_b = m x_b) and so the Ms cancel
		new_y = scale_factor*block.y
		new_height = scale_factor*block.height
		new_block = Block(0, new_y, new_height) # the x doesn't matter
		return new_block

	def trim_out_of_view(self, block:Block):
		block.top = min(block.top, self.screen.top)
		block.bottom = max(block.bottom, self.screen.bottom)

	def normalize(self, placed_object:Screen|Block):
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

	def get_partition(self, y_position, partitions) -> str:
		for i, partition in enumerate(partitions):
			if y_position in partition:
				return i
		raise ValueError("Object is outside the screen and could not be mapped")


	def project_onto_screen(self, ranges:List[ContinuousRange], block:Block):
		'''
		Projects the block onto the quantized screen
		'''
		topmost_partition_index = self.get_partition(block.top, ranges)
		bottommost_partition_index = self.get_partition(block.bottom, ranges)
		active_partitions = range(topmost_partition_index, bottommost_partition_index+1)
		return active_partitions
	
	def create_vector_from_partitions(self, active_partition_indices:list[int], resolution:int):
		vector = [0]*resolution
		for index in active_partition_indices:
			vector[index] = 1
		return vector

	def get_position_vector(self, block:Block):
		rendered_block = self.get_rendered_block(block)
		self.trim_out_of_view(rendered_block)
		self.normalize(block)
		self.normalize(self.screen)
		self.quantize()


	def get_all_position_vectors(self):
		all_vectors = []
		for block in self.blocks:
			vector = self.get_position_vector(block)
			all_vectors.append(vector)
		return all_vectors

