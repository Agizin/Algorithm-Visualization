from .internal_picture import TreePicture
from algviz.parser import structures

#a = structures.String("A", uid=2)
b = structures.String("B", uid=2)
c = structures.String("C", uid=3)
d = structures.String("D", uid=4)
leafb = structures.TreeNode(b, uid=5)
leafc = structures.TreeNode(c, uid=6)
treed = structures.TreeNode(d, [leafc], uid=7)
Tree = structures.TreeNode(leafb, [treed], uid=8)
pic = TreePicture(Tree, filename='tree.svg')
pic.draw()
pic.scale((200,500))
