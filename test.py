from bentests import asserts, test_all, testGroup

from main import Renderer, ContinuousRange


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

test_all(mainTests)