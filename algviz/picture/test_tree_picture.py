from .internal_picture import TreePicture
from algviz.parsers import structures

a = structures.String("A")
Tree = structures.TreeNode(a)
pic = TreePicture(Tree, filename='tree.svg')
pic.draw()
