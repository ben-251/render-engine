from bentests import asserts, test_all, testGroup

from main import * 

import math

from mpmath import mp, atan

mp.dps = 50



class mainTests(testGroup):
	def test_range_gen(self):
		renderer = Renderer()
		ranges = renderer.quantize(resolution=5)
		asserts.assertAlmostEquals(
			(ranges[0].start, ranges[0].stop),
			(0.0, 0.2)
		)

	def test_range_gen_two(self):
		renderer = Renderer()
		ranges = renderer.quantize(resolution=10)
		asserts.assertAlmostEquals(
			(ranges[2].start, ranges[2].stop),
			(0.2, 0.3)
		)

	def test_get_rendered_block(self):
		block = Block(1, 0.35, 0.25)
		renderer = Renderer()
		block = renderer.get_rendered_block(block)

		asserts.assertAlmostEquals(
			[block.x, block.y, block.height, block.top, block.bottom],
			[0, 0.7, 0.5, 0.95, 0.45],
			3
		)

	def test_trim_top(self):
		block = Block(1, 0.35, 0.25)
		renderer = Renderer()
		block = renderer.get_rendered_block(block)
		renderer.trim_out_of_view(block)

		asserts.assertAlmostEquals(
			[block.x, block.y, block.height, block.top, block.bottom],
			[0, 0.7, 0.5, 2*0.414214, 0.45],
			4
		)

	def test_trim_both(self):
		block = Block(0.17, -0.012, 0.25)
		renderer = Renderer()
		block = renderer.get_rendered_block(block)
		renderer.trim_out_of_view(block)

		asserts.assertAlmostEquals(
			[block.x, block.y, block.height, block.top, block.bottom],
			[0, -0.141176470588, 2.94117647059, 2*0.414214, -2*0.414214],
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

	# def test_render(self):
	# 	blocks = [
	# 		Block(1.023, 0.237,1)
	# 	]
	# 	renderer = Renderer(blocks=blocks)
	# 	renderer.render(500)

test_all(mainTests)