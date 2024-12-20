from os import write
from PIL import Image
from imageio.typing import ArrayLike
from backend import Block, Renderer, Camera
from typing import List, Tuple, cast, Optional
import numpy as np
from numpy.typing import NDArray
import imageio

# List of PIL images
def get_renders() -> List[Image.Image]:
	images = []
	for y in range(100):
		blocks = [
			Block(x=1.72,y=0.3,height=0.072, color=(255,0,0)),
			Block(x=1.726,y=-0.22+(y/100),height=0.072, color=(0,255,255-y)),
			Block(x=5, y=0, height=100, color=(255,205,50)), # should essentially form a background
			Block(x=1, y=45, height=0.4, color=(0,255,0)), # should not show
			Block(x = 1.73, y=0.25, height=0.25, color=(100,125,255))
		]
		renderer = Renderer(blocks=blocks, camera=Camera(forced_screen_height=1))
		renderer.generate_all_position_vectors()
		image = renderer.generate_image(renderer.blocks, (50,250))
		images.append(image)
	return images

images = get_renders()

# Convert PIL images to numpy arrays
frames = [np.array(img) for img in images]

# Save as a video
imageio.mimwrite("outputs/output.mp4", cast(List[ArrayLike], frames), fps=30)


class Animator(Renderer):
	def __init__(self, blocks:List[Block]) -> None:
		for i, block in enumerate(blocks):
			block.id=i
		super().__init__(blocks=blocks, camera=Camera(forced_screen_height=1))

	def slide(self, block_id:int, start:Tuple[float,float], end:Tuple[float,float], frame_count:int):
		target_block = self.retrieve_block_from_id(block_id)
		inbetweens = self.generate_inbetweens(frame_count, target_block, start, end)
		self.make_video_from_frames(inbetweens,write_path="")

	def generate_inbetweens(self, frame_count:int, target_block:Block, start:Tuple[float,float], end:Tuple[float,float]):
		target_block.x, target_block.y = start
		x_steps:List[float] = np.linspace(start[0], end[0], frame_count).tolist() # type:ignore
		y_steps:List[float] = np.linspace(start[1], end[1], frame_count).tolist() # type:ignore
		inbetweens:List[Image.Image] = []

		for x_position, y_position in zip(x_steps, y_steps):
			target_block.x = x_position
			target_block.y = y_position
			self.generate_all_position_vectors()
			image = self.generate_image(self.blocks, (100,500))
			inbetweens.append(image)

		return inbetweens
	
	def make_video_from_frames(self, raw_frames:List[Image.Image], fps=30, write_path:Optional[str]=None):
		write_path = "outputs/output.mp4" if write_path is None else "outputs/" + write_path

		frames = [np.array(frame) for frame in raw_frames]
		imageio.mimwrite("outputs/output.mp4", cast(List[ArrayLike], frames), fps=30)

		


