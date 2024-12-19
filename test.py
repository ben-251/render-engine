# type:ignore

from bentests import asserts, test_all, testGroup
from backend import * 
import math
from mpmath import mp, atan
import numpy as np

mp.dps = 50

class mainTests(testGroup):
	def test_get_rendered_block(self):
		block = Block(1, 0.35, 0.25)
		renderer = Renderer()
		block = renderer.get_rendered_block(block)

		asserts.assertAlmostEquals(
			[block.x, block.y, block.height, block.top, block.bottom],
			[1, 0.7, 0.5, 0.95, 0.45],
			3
		)

	def test_trim_top(self):
		block = Block(1, 0.35, 0.25)
		renderer = Renderer()
		block = renderer.get_rendered_block(block)
		renderer.trim_out_of_view(block)

		asserts.assertAlmostEquals(
			[block.x, block.y, block.height, block.top, block.bottom],
			[1, 0.7, 0.5, 2*0.414214, 0.45],
			4
		)

	def test_trim_both(self):
		block = Block(0.17, -0.012, 0.25)
		renderer = Renderer()
		block = renderer.get_rendered_block(block)
		renderer.trim_out_of_view(block)

		asserts.assertAlmostEquals(
			[block.x, block.y, block.height, block.top, block.bottom],
			[0.17, -0.141176470588, 2.94117647059, 2*0.414214, -2*0.414214],
			4
		)

	# def test_forced_screen_height(self):
	# 	camera_ang = 2*atan(0.3)
	# 	camera = Camera(theta = camera_ang)
	# 	asserts.assertAlmostEquals(
	# 		camera.m * 2,
	# 		0.3
	# 	)
	def test_gradient_from_theta(self):
		camera = Camera(theta=0.5)
		asserts.assertAlmostEquals(float(camera.m), 0.2553419212, 5)

	def test_proj_screen_height_from_theta(self):
		camera = Camera(theta=0.5)
		proj_screen = ProjectionScreen(camera)
		asserts.assertAlmostEquals(float(proj_screen.top), 0.5106838424)

	def test_gradient_from_forced_height(self):
		cam = Camera(forced_screen_height=1)
		proj_screen = ProjectionScreen(cam)
		asserts.assertEquals(
			float(proj_screen.height),
			1
		)

	def test_default_theta(self):
		camera = Camera()
		proj_screen = ProjectionScreen(camera)
		asserts.assertAlmostEquals(float(proj_screen.top), 0.8284271247, 6)

	def test_theta_and_forced_height(self):
		with asserts.assertRaises(ValueError):
			camera = Camera(theta=0.5,forced_screen_height=1)

	def test_scale_to_one(self):
		camera = Camera(forced_screen_height=1)
		renderer = Renderer(camera = camera)

		block = Block(1, 0, 0.25)
		rendered_block = renderer.get_rendered_block(block)
		renderer.trim_out_of_view(rendered_block)
		renderer.scale_to_one(rendered_block)

		asserts.assertAlmostEquals(
			list(map(float, [rendered_block.y, rendered_block.top, rendered_block.bottom, rendered_block.height])),
			[0, 0.25, -0.25, 0.5],
			4
		)

	def test_normalise_screen_with_big_object(self):
		block = Block(0.17, -0.012, 0.25)
		camera = Camera(forced_screen_height=1)
		renderer = Renderer(camera=camera)
		block = renderer.get_rendered_block(block)
		renderer.trim_out_of_view(block)
		renderer.normalize(block)

		asserts.assertAlmostEquals(
			list(map(float, [
				renderer.projected_screen.y,
				renderer.projected_screen.height,
				renderer.projected_screen.top,
				renderer.projected_screen.bottom
			])),
			[0, 1, 0.5, -0.5],
			4
		)

	def test_projected_screen_small(self):
		camera = Camera(forced_screen_height=2)
		renderer = Renderer(camera=camera)
		asserts.assertAlmostEquals(
			list(map(float, [
				renderer.projected_screen.y,
				renderer.projected_screen.height,
				renderer.projected_screen.top,
				renderer.projected_screen.bottom
			])),
			[0, 2, 1, -1],
			4
		)	

	def test_normalise_big_object(self):
		block = Block(0.17, -0.012, 0.25)
		cam = Camera(forced_screen_height=1)
		renderer = Renderer(camera=cam)
		block = renderer.get_rendered_block(block)
		renderer.trim_out_of_view(block)
		renderer.normalize(block)

		asserts.assertAlmostEquals(
			list(map(float, [block.y, block.top, block.bottom])),
			[0.5-0.141176470588, 1, 0],
			4
		)

	def test_normalise_contained_object(self):
		camera = Camera(forced_screen_height=1)
		renderer = Renderer(camera = camera)

		block = Block(1, 0, 0.25)
		rendered_block = renderer.get_rendered_block(block)
		renderer.trim_out_of_view(rendered_block)
		renderer.normalize(rendered_block)

		asserts.assertAlmostEquals(
			list(map(float, [rendered_block.y, rendered_block.top, rendered_block.bottom, rendered_block.height])),
			[0.5, 0.5+0.25, 0.5-0.25, 0.5],
			4
		)

	def test_normalise_half_contained_object(self): 
		camera = Camera(forced_screen_height=1)
		renderer = Renderer(camera = camera)

		block = Block(1, 0.2, 0.25)
		rendered_block = renderer.get_rendered_block(block)
		renderer.trim_out_of_view(rendered_block)
		renderer.normalize(rendered_block)

		asserts.assertAlmostEquals(
			list(map(float, [rendered_block.y, rendered_block.height, rendered_block.top, rendered_block.bottom])),
			[0.9, 0.5, 1, 0.15+0.5],
			4
		)

class continuousRangeTests(testGroup):
	def test_contains(self):
		range_  = ContinuousRange(0.1, 0.2)
		asserts.assertEquals(
			0.12536251 in range_,
			True
		)

	def test_not_contains(self):
		range_  = ContinuousRange(0.1, 0.2)
		asserts.assertEquals(
			0.045 in range_,
			False
		)

	def test_contains_but_negative(self):
		range_  = ContinuousRange(-0.15, -0.1)
		asserts.assertEquals(
			-0.143 in range_,
			True
		)
class projectionTests(testGroup):
	def test_quantize(self):
		renderer = Renderer()
		ranges = renderer.quantize(resolution=5)
		asserts.assertAlmostEquals(
			(ranges[0].start, ranges[0].stop),
			(0.0, 0.2)
		)

	def test_range_quantize_again(self):
		renderer = Renderer()
		ranges = renderer.quantize(resolution=10)
		asserts.assertAlmostEquals(
			(ranges[2].start, ranges[2].stop),
			(0.2, 0.3)
		)

	def test_find_projected_slice(self):
		renderer = Renderer()
		ranges = renderer.quantize(resolution=5)
		y_position = 0.25
		location = renderer.find_projected_partition(y_position, ranges)
		asserts.assertEquals(
			location,
			1
		)	
	
	def test_find_projected_slice_exact(self):
		renderer = Renderer()
		ranges = renderer.quantize(resolution=5)
		y_position = 0.2
		location = renderer.find_projected_partition(y_position, ranges)
		asserts.assertEquals(
			location,
			0 # it's in two sections but we go with the first, so the lower one (which will be fine with many pixels)
		)	

	def test_fail_to_find_projected_slice(self):
		with asserts.assertRaises(ValueError):
			renderer = Renderer()
			ranges = renderer.quantize(resolution=5)
			y_position = 1.02
			location = renderer.find_projected_partition(y_position, ranges)
	

	def test_fail_to_find_projected_slice_negative(self):
		with asserts.assertRaises(ValueError):
			renderer = Renderer()
			ranges = renderer.quantize(resolution=5)
			y_position = -0.4
			location = renderer.find_projected_partition(y_position, ranges)

	def test_project_onto_range_contained(self):
		block = Block(0,0.2,0.2)
		renderer = Renderer()
		ranges = renderer.quantize(resolution=10)
		values = renderer.project_onto_screen(ranges, block)
		asserts.assertEquals(values,
			[0,1,2]
		)

	def test_project_onto_range_partly_out_of_screen(self):
		initial_block = Block(2,0.4,0.96)
		renderer = Renderer(camera=Camera(forced_screen_height=1))
		block = renderer.get_rendered_block(initial_block)
		renderer.trim_out_of_view(block)
		renderer.normalize(block)
		ranges = renderer.quantize(resolution=5)
		values = renderer.project_onto_screen(ranges, block)
		asserts.assertEquals(values,
			[2,3,4]
		)

	def test_create_vector_from_slices(self):
		initial_block = Block(2,0.4,0.96)
		renderer = Renderer(camera=Camera(forced_screen_height=1))
		block = renderer.get_rendered_block(initial_block)
		renderer.trim_out_of_view(block)
		renderer.normalize(block)
		ranges = renderer.quantize(resolution=5)
		values = renderer.project_onto_screen(ranges, block)
		vector = renderer.create_vector_from_partitions(values, 5, block.color)

		asserts.assertEquals(
			vector,
			[BG,BG,BLACK,BLACK,BLACK]
		)	

	# def test_add_vectors(self):
	# 	block1 = Block(0,0,0)
	# 	block2 = Block(0,0,0)
	# 	block1.vector = np.array([0,0,1,1,1])
	# 	block2.vector = np.array([1,0,1,0,0])

	# 	renderer = Renderer(blocks=[block1, block2])
	# 	sum_ = renderer.combine_vectors()
	# 	asserts.assertEquals(
	# 		sum_,
	# 		np.array([1,0,2,1,1])
	# 	)

class colorTests(testGroup):
	def testGetColorMap(self):
		#TODO: make this pass 
		resolution = 4
		blockA = Block(1, 0.75, 0.25, color=(255,255,0)) # Yellow
		blockB = Block(2, 0.6, 0.24, color=(255, 0, 0)) # Red 
		blockC = Block(3, 0.8, 0.4, color=(255, 125, 0)) # Orange
		blockD = Block(4, 0.8, 0.2, color=(0, 125, 255)) # Blue

		# technically doing the projection computation for it but there are tests for this already
		blockA.vector = [1,1,0,0]
		blockB.vector = [0,1,1,0]
		blockC.vector = [1,1,0,0]
		blockD.vector = [1,0,0,0]

		blocks = [blockA, blockB, blockC, blockD]

		renderer = Renderer(camera=Camera(forced_screen_height=1))
		vector = renderer.generate_color_vector(blocks, 4)
		asserts.assertEquals(
			vector,
			[
				(255,255,0),
				(255,255,0),
				(255,255,0),
				(255,255,255)
			]
		)
test_all(mainTests, continuousRangeTests, projectionTests, colorTests)