import numpy as np

def notCommonElements(list1, list2):
    result = []
    for element in list1:
        if element not in list2:
            result.append(element)        
    return result

# Check node function
class CheckNode:
    def __init__(self, name, index):
        self.degree = 0
        self.connectedNodes = []
        self.name = name
        self.index = index
    
    def __repr__(self) -> str:
        return "name: {name} degree: {degree}\n".format(name = self.name, degree=self.degree)
    
    def addConnectedNode(self, node):
        self.connectedNodes.append(node)

# Variable node function 
class VariableNode:
    def __init__(self, name, degree, index):
        self.degree = degree
        self.connectedNodes = []
        self.name = name
        self.index = index
    
    def __repr__(self) -> str:
        return "name: {name} degree: {degree}\n".format(name = self.name, degree=self.degree)
    
    def addConnectedNode(self, node):
        self.degree += 1
        self.connectedNodes.append(node)

# Tanner graph function
class Tannergraph:
    def __init__(self, m, n, Dv):
        self.Hmatrix = np.zeros((m,n))
        self.checkNodes = [CheckNode("C" + str(i), i) for i in range(0, m)]
        self.variableNodes = [VariableNode("V" + str(i), Dv, i) for i in range(0,n)]

    
    def addEdge(self, checkNodeIndex, variableNodeIndex):
        self.Hmatrix[checkNodeIndex, variableNodeIndex] = 1
        self.checkNodes[checkNodeIndex].degree += 1
        self.variableNodes[variableNodeIndex].connectedNodes.append(self.checkNodes[checkNodeIndex])
        self.checkNodes[checkNodeIndex].connectedNodes.append(self.variableNodes[variableNodeIndex])
       


    def findLowestDegreeCheckNode(self): #choosing according to index
        lowest = self.checkNodes[0]
        for current in self.checkNodes:
            if current.degree < lowest.degree:
                lowest = current
            # possibly
            #elseif current.degree = lower.degree:
                #add to a list and then choose at random for RANDPEG
            else:
                pass 
        return lowest
    
    def getSubTree(self, depth, index):
        return SubTree(self, depth, self.variableNodes[index])

# Subtree function
class SubTree:
    def __init__(self, tannergraph, depth, rootNode):
        self.tannergraph = tannergraph
        self.depth = depth
        self.rootNode = rootNode
        self.rootNodeIndex = rootNode.index
        
        level = 0
        queue = [self.rootNode]
        usedNodes = [self.rootNode]

        while(len(queue)!= 0 and level < depth):
            level += 1
            levelQueue = []

            for node in queue:
                children = notCommonElements(node.connectedNodes, usedNodes)
                usedNodes += children
                levelQueue += children
            queue = levelQueue
        self.level = level
        self.usedNodes = usedNodes
    
    def coveredCheckNodes(self):
        coveredCheckNodes = []
        for node in self.usedNodes:
            if(type(node) == CheckNode):
                coveredCheckNodes.append(node)
            else:
                pass
        return coveredCheckNodes

    def allCheckNodesCovered(self):
        coveredCheckNodes = self.coveredCheckNodes()
        if(len(coveredCheckNodes) == len(self.tannergraph.checkNodes)):
            return True
        else:
            return False      
    
    def findLowestDegreeCheckNode(self):
        nodes = self.coveredCheckNodes()
        checkNodes = notCommonElements(self.tannergraph.checkNodes, nodes)
        lowest = checkNodes[0]
        for node in checkNodes:
            if(node.degree < lowest.degree):
                lowest = node
            elif(node.degree == lowest.degree):
                if(node.index < lowest.index):
                    lowest = node
        return lowest