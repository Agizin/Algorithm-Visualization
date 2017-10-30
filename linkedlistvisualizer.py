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

	def length(self):
		current = self.start
		count = 0;
		while(current is not None):
			count += 1
			current = current.nextnode
		return count

def draw_contents(svg_doc = None, item = None, center = None):#universal drawer; figures out which function to use to draw the requested item
	if type(item) == int:
		draw_integer(svg_doc, item, center)
	elif type(item) == LinkedList:
		draw_linkedlist(svg_doc, item, center)

def draw_integer(svg_doc = None, item = None, center = None):
	text = svg_doc.text(text = str(item), insert = center)
	svg_doc.add(text)

def draw_linkedlist(svg_doc = None, ll = None, center = None):
	if(svg_doc is None):
		length = str(ll.length() * 100) + "px" #unless given an svgdoc, default size is 100 * ll's length by 400
		svg_doc = svgwrite.Drawing(filename = 'linkedlist.svg', size = [length, '400px'])
		center = [50, 200]
	current = ll.start
	for i in range(0, ll.length()):
		circle = svg_doc.circle(center = center, r = 40, stroke_width = '3', stroke = 'black', fill = 'white')
		edge = svg_doc.line(start = [center[0] + 40, center[1]], end = [center[0] + 60, center[1]], stroke_width = '3', stroke = 'black')
		svg_doc.add(circle)
		if current.nextnode is not None:#do not add edge on the last node
			svg_doc.add(edge)
		draw_contents(svg_doc, current.value, center)
		current = current.nextnode#go to next node
		center[0] += 100#x coord of center moves right 100 px each iteration
	svg_doc.save()

if __name__ == "__main__":
	ll = LinkedList()
	n5 = Node(5, None)
	n4 = Node(4, n5)
	n3 = Node(3, n4)
	n2 = Node(2, n3)
	n1 = Node(1, n2)
	ll.addNode(n1)

	draw_contents(item = ll)
