# https://www.desmos.com/calculator/2o5u3ueaqb

import math
from PIL import Image
import numpy as np
from typing import Final, List, Optional, Sequence, Tuple, TypeAlias
from mpmath import mp, tan, atan
from numpy.typing import NDArray

mp.dps = 50  
Color: TypeAlias = Tuple[int,int,int]
Vec: TypeAlias = Sequence[Color]
BG:Color = (255,255,255)
BLACK:Color= (0,0,0)

class OutOfRangeError(Exception): ...
class NotFounderror(Exception): ...


class ContinuousRange:
	def __init__(self, start:float, stop:float):
		if start > stop:
			raise ValueError("start must be less than or equal to stop")
		self.start = start
		self.stop = stop


	def __contains__(self, value:float|int) -> bool:
		return self.start <= value <= self.stop

class Camera:
	x:float
	y:float

	def __init__(
			self,
			x:Optional[float]=None,
			y:Optional[float]=None,
			theta:Optional[float]=None,
			forced_screen_height:Optional[float]=None
		) -> None:

		assigned_theta:float = 0.0
		if (theta is None) and (not forced_screen_height is None): 
			assigned_theta = 2*atan(forced_screen_height/4)
		elif (not theta is None) and (forced_screen_height is None):
			assigned_theta = theta
		elif theta is None and forced_screen_height is None:
			assigned_theta = math.pi/4
		else:
			raise ValueError("Theta and forced_screen_height can't both be set")
		
		if x is None:
			x = 0
		if y is None:
			y = 0

		self.x = x
		self.y = y
		self.theta:float = assigned_theta
		self.m = tan(0.5 * self.theta)

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
	def __init__(self,
		x:float,
		y:float,
		height:float,
		color:Optional[Tuple[int,int,int]]=None,
		id:Optional[int]=None
	) -> None:
		self.x:float = x
		self.y:float = y
		self.height:float = height
		self.top:float = self.y + 0.5*self.height
		self.bottom:float = self.y - 0.5*self.height
		self.vector:Vec = []
		self.color:Tuple[int,int,int] = (0,0,0) if color is None else color
		self.id = id

class Renderer:
	def __init__(self, blocks:Optional[List[Block]]=None, camera:Optional[Camera]=None) -> None:
		self.camera = Camera() if camera is None else camera
		self.screen = Screen()
		self.blocks:List[Block] = [] if blocks is None else blocks
		self.projected_screen = ProjectionScreen(self.camera)
		self.bg_color = BG

	def retrieve_block_from_id(self, block_id:int):
		for block in self.blocks:
			if block.id == block_id:
				return block
		raise NotFounderror
				

	def get_all_vectors(self, blocks:Optional[List[Block]]) -> List[Vec]:
		blocks = self.blocks if blocks is None else blocks
		return [block.vector for block in blocks]

	def get_rendered_block(self,block:Block):
		scale_factor = self.projected_screen.x / block.x # (y_p = m x_p) / (y_b = m x_b) and so the Ms cancel
		new_y = scale_factor*block.y
		new_height = scale_factor*block.height
		new_block = Block(block.x, new_y, new_height) # the x doesn't matter
		return new_block

	def trim_out_of_view(self, block:Block):
		# set top and bottom to top if they're higher than top, and bottom if lower than bottom wait no better to just catch the "out of screen" error while rendering
		block.top = min(block.top, self.projected_screen.top)
		block.bottom = max(block.bottom, self.projected_screen.bottom)

	def normalize(self, placed_object:Screen|Block):
		#TODO: before adding 0.5, we need to make sure it's actually -1 to 1, so we scale everything down to the size of the projected screen
		self.scale_to_one(placed_object)
		self.y_translate(placed_object, 0.5)

	def scale_to_one(self, placed_object:Screen|Block):
		placed_object.y /= self.projected_screen.height
		placed_object.top /= self.projected_screen.height
		placed_object.bottom /= self.projected_screen.height
		placed_object.height /= self.projected_screen.height

	def y_translate(self, placed_object:Screen|Block, amount:float):
		placed_object.y += amount
		placed_object.top += amount
		placed_object.bottom += amount

	
	def quantize(self, resolution:int=5) -> List[ContinuousRange]:
		'''
		`resolution`: number of slices to cut the slider (screen) into.
					 Higher number results in a less pixelated render

		returns a list of ranges (slices). 
		example with 5 partitions:
			(0,0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8,1.0)
		'''
		ranges:List[ContinuousRange] = []
		range_size = 1/resolution # e.g, 0.2
		for i in range(resolution):
			new_range_start = i * range_size # for example 0*0.2, 1*0.2, etc
			new_range_end = new_range_start + range_size
			ranges.append(ContinuousRange(new_range_start, new_range_end))
		return ranges

	def find_projected_partition(self, y_position:float, partitions:List[ContinuousRange]) -> int:
		for i, partition in enumerate(partitions):
			if y_position in partition:
				return i
		raise OutOfRangeError("Object is outside the screen and could not be mapped")

	def project_onto_screen(self, ranges:List[ContinuousRange], block:Block) -> List[int]:
		'''
		Projects the block onto the quantized screen by returning all the partitions that have a value
		'''
		try:
			topmost_partition_index = self.find_projected_partition(block.top, ranges)
			bottommost_partition_index = self.find_projected_partition(block.bottom, ranges)
		except OutOfRangeError:
			return []
		active_partitions = list(range(bottommost_partition_index, topmost_partition_index+1))
		return active_partitions
	
	def create_vector_from_partitions(self, active_partition_indices:list[int], dimension:int, color) -> List[Tuple[int,int,int]]:
		vector:List[Tuple[int,int,int]] = [self.bg_color] * dimension
		for index in active_partition_indices:
			vector[index] = color 
		return vector

	def generate_position_vector(self, block:Block, dimension:Optional[int]=None) -> Vec:
		dimension = 5 if dimension is None else dimension
		rendered_block = self.get_rendered_block(block)
		self.trim_out_of_view(rendered_block)
		self.normalize(rendered_block)
		ranges = self.quantize(dimension)
		active_partitions = self.project_onto_screen(ranges, rendered_block)
		vector = self.create_vector_from_partitions(active_partitions, dimension, block.color)
		return vector
	

	def generate_color_vector(self, blocks:List[Block],dim:int) -> Vec:
		final_vec = [self.bg_color]*dim
		sorted_blocks = sorted(blocks, key=lambda block: block.x, reverse=True)
		for i in range(dim):
			for block in sorted_blocks:
				if block.vector[i] != self.bg_color:
					final_vec[i] = block.color
		return final_vec[::-1]

	def generate_all_position_vectors(self, resolution:Optional[int]=None) -> None:
		resolution = 1000 if resolution is None else resolution
		for block in self.blocks:
			vector = self.generate_position_vector(block, resolution)
			block.vector = vector

	# def combine_vectors(self, blocks:Optional[List[Block]]=None) -> List[Tuple[int,int,int]]:
	# 	#TODO: include colours
	# 	blocks = self.blocks if blocks is None else blocks
	# 	vectors = self.get_all_vectors(blocks=blocks)
	# 	result_vector = sum(vectors, [self.bg_color]*len(vectors[0]))
	# 	return result_vector

	def generate_image(self, blocks, image_size:Optional[Tuple[int,int]]=None) -> Image.Image:
		# At each level along all vectors, see which is closest to the screen
		# then set the colour for that pixel to the frontmost colour.
		image_size = (100,500) if image_size is None else image_size
		vectors = self.get_all_vectors(blocks)
		dimension = len(vectors[0])

		initial_image = Image.new(mode="RGB",size=(1, dimension))

		color_map = self.generate_color_vector(blocks, dimension)
		initial_image.putdata(list(color_map)) #type: ignore (it's pedantic cuz PIL is vague)

		rescaled_image = initial_image.resize((image_size[0],image_size[1]), resample=Image.Resampling.NEAREST)
		
		return rescaled_image

	def render(self, image_size:Optional[Tuple[int,int]]=None):
		self.generate_all_position_vectors()
		self.generate_image(self.blocks, image_size).show()


