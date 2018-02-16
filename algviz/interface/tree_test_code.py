class TreeNode:
    def __init__(self, data):
        self.children = []
        if isinstance(data, list):
            self.data = data[0]
        else:
            self.data = data
        if isinstance(data, list):
            for i in range(1, len(data)):
                if isinstance(data[i], list):
                    ntn = TreeNode(data[i])
                    ntn.data = data[0]
                    self.children.append(TreeNode(data[i]))
                else:
                    self.children.append(TreeNode(data[i]))

    def isleaf(self):
        if len(self.children) == 0:
            return True
        else:
            return False

    def isbinary(self):
        if len(self.children) == 0:
            return True
        if len(self.children) == 1:
            return self.children[0].isbinary()
        if len(self.children) > 2:
            return False
        if len(self.children) == 2:
            return self.children[0].isbinary() and self.children[1].isbinary()


    def infix(self):
        if len(self.children) == 0:
            return str(self.data)
        if len(self.children) == 1:
            return str(self.data) + str(self.children[0].infix())
        if len(self.children) == 2:
            return "(" + str(self.children[0].infix()) + " " + str(self.data) + " " + str(self.children[1].infix()) + ")"

    def tostring(self, level = 0):
        s = [("  " * level) + str(self.data)]
        for c in self.children:
            s.append(c.tostring(level + 1))
        return "\n".join(s)

class Tree:
    def __init__(self):
        self.root = None

    def fromlists(self, lists):
        self.root = TreeNode(lists)

    def infix(self):
        return self.root.infix()

    def isbinary(self):
        return self.root.isbinary()

    def __str__(self):
        return(self.root.tostring())
