import svgwrite
class Node:
	def __init__(self, value = None, nextnode = None):
		self.value = value
		self.nextnode = nextnode

	def setValue(self, value):
		self.value = value

	def setNext(self, nextnode):
		self.nextnode = nextnode

class LinkedList:
	def __init__(self, start = None):
		self.start = start

	def addNode(self, node):
		current = self.start
		if(self.start is None):
			self.start = node
		else:
			while(current.nextnode is not None):
				current = current.nextnode
			current.nextnode = node#add the node

#	def length(self):
#		current = self.start
#		count = 0;
#		while(current is not None):
#			count += 1
#			current = current.nextnode
#		return count

	def __iter__(self):
		self.i = self.start
		return self

	def __next__(self):
		if self.i is None:
			raise StopIteration
		else:
			item = self.i.value
			self.i = self.i.nextnode
			return item

class BaseVisualizer:
	def __init__(self, svg_doc = None):
		self.svg_doc = svg_doc

	def save(self):
		if self.svg_doc is not None:
			self.svg_doc.save()

	def length(self, item):
		length = 0
		for i in item:
			length += 1
		return length

	def draw_contents(self, item = None, svg_doc = None, center = None, nested = False, getSize = False):#universal drawer; figures out which function to use to draw the requested item
		if type(item) == int:
			return self.draw_string(item, svg_doc, center, nested, getSize)
		elif type(item) == LinkedList:
			return self.draw_linkedlist(item, svg_doc, center, nested, getSize)

	def draw_string(self, item, svg_doc = None, center = None, nested = False, getSize = False):
		size = 30 * len(str(item))#might be too complicated to have this be passed as an arg between funcs
		offset = 0
		if nested:
			offset = size / 2
		if not getSize:#draw unless we're getting the size	
			svg_doc.add(svg_doc.text(text = str(item), insert = [center[0] - offset/2, center[1] + (offset / len(str(item)) / 2)], font_size = 30))
		return size

	def draw_linkedlist(self, ll, svg_doc = None, center = None, nested = False, getSize = False):
		size = 0
		length = self.length(ll)
		offset_array = []
		radius = 40#default radius size
		if(self.svg_doc is None and not getSize):#note, default length can be overflowed as it stands, need to come up with a better way of determining length
			center = [radius * 2.5, 200]
			value = self.draw_contents(ll, self.svg_doc, center, getSize = True)#how long should our document be?
			doc_length = str(value + 100) + "px" #unless given an svgdoc, default size is 150 * ll's length by 400
			self.svg_doc = svgwrite.Drawing(filename = 'linkedlist.svg', size = [doc_length, '400px'])
		center = [center[0],center[1]]#if its nested, this prevents changes to this center from affecting the original
		if nested:#shift the center to the left by the size of what we will draw divided by two
			tempOffset = self.draw_contents(ll, self.svg_doc, center, nested = False, getSize = True)
			center[0] -= tempOffset/6#this offset for nested lists might need adjusting...
		originalCenter = [center[0],center[1]]#so the two aren't connected (Changing one wont change the other now)
		for i in ll:#draw nodes
			offset = self.draw_contents(i, self.svg_doc, center, nested = True, getSize = True)#to get size, this will need to be replaced later with a function to just receive size w/o drawing
			offset -= radius #only expand the bubble if its contents are greater than radius in size
			if offset < 0:
				offset = 0
			offset_array.append(offset)
			if nested:#note: this needs to be implemented better, i think we need more arguments to do this right, but for now i didn't want to overload on them
				center[0] += offset/4
				if not getSize:
					self.svg_doc.add(self.svg_doc.ellipse(center = center, r = [radius/2 + offset/4,  radius/2], stroke_width = '3', stroke = 'black', fill = 'white'))
					self.draw_contents(i, self.svg_doc, center, nested = True)
				center[0] += 1.25*radius + offset/4#x coord of center moves right 100 + offset//2 px each iteration, we added offset earlier
				size += 1.25*radius + offset/2
			else:
				center[0] += offset/2
				if not getSize:
					self.svg_doc.add(self.svg_doc.ellipse(center = center, r = [radius + offset/2, radius], stroke_width = '3', stroke = 'black', fill = 'white'))
					self.draw_contents(i, self.svg_doc, center, nested = True)
				center[0] += 2.5 *radius + offset/2#x coord of center moves right 100 + offset//2 px each iteration, we added offset earlier
				size += 2.5*radius + offset
		center = originalCenter#this is whatever the original center for the first node is
		for i in range(0, len(offset_array)):#add edges
			if i != length - 1:#dont add an edge on the last one
				if nested:
					center[0] += offset_array[i] / 4
					if not getSize:
						self.svg_doc.add(self.svg_doc.line(start = [center[0] + radius/2 + offset_array[i]/4, center[1]], end = [center[0] + (3 * radius) / 4 + offset_array[i]/4, center[1]], stroke_width = '3', stroke = 'black'))
					center[0] += radius*1.25 + offset_array[i]/4
				else:
					center[0] += offset_array[i]/2
					if not getSize:
						self.svg_doc.add(self.svg_doc.line(start = [center[0] + radius + offset_array[i]/2, center[1]], end = [center[0] + (3 * radius) / 2 + offset_array[i]/2, center[1]], stroke_width = '3', stroke = 'black'))
					center[0] += 2.5*radius + offset_array[i]/2
		self.save()
		return size

	def __str__(self):
		return self.svg_doc.tostring()

class LLVisualiser(BaseVisualizer):
	def __init__(self, svg_doc = None):
		self.svg_doc = svg_doc

	def _draw(self, ll, center = None, nested = False, getSize = False):
		self.draw_contents(item = ll)

if __name__ == "__main__":
	ll = LinkedList()
	ll2 = LinkedList()
	n7 = Node(4, None)
	n6 = Node(111, n7)
	n8 = Node(0, n6)
	ll2.addNode(n8)
	n5 = Node(321, None)
	n4 = Node(144123, n5)
	n3 = Node(ll2, n4)
	n2 = Node(2232, n3)
	n1 = Node(123, n2)
	ll.addNode(n1)


	t = LLVisualiser()
	t._draw(ll)
