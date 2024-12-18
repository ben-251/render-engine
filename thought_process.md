# Color Information
we have some vectors, say `[1,1,0,0,0]` and `[0,0,0,0,1]`, generated from two different blocks, each with a colour.


```python
class Block:
	vector:nparrything #computed by Renderer 
	rgb_color:tuple # specifically a triple

class Renderer:
	...
	def generate_vector_from_block(block:Block) -> nparray: ...
```