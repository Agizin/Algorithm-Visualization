from .picture import TreePicture
from algviz.parser import structures

a = structures.String("AAAAAAAA", uid=1)
b = structures.String("BBBBBb", uid=2)
c = structures.String("CCCCCCCCccc", uid=3)
d = structures.String("DDDD", uid=4)
leafb = structures.TreeNode(b, uid=5)
leafc = structures.TreeNode(c, uid=6)
treed = structures.TreeNode(d, [leafb, leafc], uid=7)
Tree = structures.TreeNode(a, [treed], uid=8)
pic = TreePicture(Tree)
pic.draw()
pic.save("tree.svg")
