from backend import Renderer, Block, Camera, tan

def test_render():
	blocks = [
		Block(x=2,y=0.4,height=0.96)
	]
	renderer = Renderer(blocks=blocks, camera=Camera(forced_screen_height=1))
	renderer.render()

def try_with_two_blocks():
	blocks = [
		Block(x=1.72,y=0.37,height=0.072),
		Block(x=1.956,y=-0.22,height=0.072)
	]
	renderer = Renderer(blocks=blocks, camera=Camera(forced_screen_height=1))
	renderer.render()

def try_new():
	blocks = [
		Block(x=1.72,y=0.3,height=0.072, color=(255,0,0)),
		Block(x=2.956,y=-0.22,height=0.072, color=(0,255,255)),
		Block(x=5, y=0, height=100, color=(255,205,50)), # should essentially form a background
		Block(x=1, y=45, height=0.4, color=(0,255,0)), # should not show
		Block(x = 1.73, y=0.25, height=0.25, color=(100,125,255))
	]
	renderer = Renderer(blocks=blocks, camera=Camera(forced_screen_height=1))
	renderer.render()
try_new()