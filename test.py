from bentests import asserts, test_all, testGroup

from main import * 


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

	# def test_render(self):
	# 	blocks = [
	# 		Block(1.023, 0.237,1)
	# 	]
	# 	renderer = Renderer(blocks=blocks)
	# 	renderer.render(500)

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

	def test_normalise_screen(self):
		block = Block(1, 0.35, 0.25)
		renderer = Renderer()
		block = renderer.get_rendered_block(block)
		renderer.trim_out_of_view(block)

		asserts.assertAlmostEquals(
			[block.x, block.y, block.height, block.top, block.bottom],
			[0, 0.7, 0.5, 2*0.414214, 0.45],
			4
		)
test_all(mainTests)