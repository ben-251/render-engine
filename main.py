from backend import Renderer, Block, Camera

def test_render():
	blocks = [
		Block(x=2,y=0.4,height=0.96)
	]
	renderer = Renderer(blocks=blocks, camera=Camera(forced_screen_height=1))
	renderer.render(500)

def try_with_two_blocks():
	blocks = [
		Block(x=1.72,y=0.37,height=0.072),
		Block(x=1.956,y=-0.22,height=0.072)
	]
	renderer = Renderer(blocks=blocks, camera=Camera(forced_screen_height=1))
	renderer.render(500)

# test_render()
try_with_two_blocks()