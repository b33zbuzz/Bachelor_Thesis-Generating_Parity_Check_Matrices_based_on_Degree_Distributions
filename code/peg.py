import numpy as np
from tannergraph import Tannergraph
import scipy.io
import h5py

m= int(input("Number of Check Nodes: "))
n = int(input("Number of Variable Nodes: "))
#create H matrix
Hmat = np.zeros((m,n))
# creating an empty list for variable nodes degree distribution
Dv = int(input("Variable Node degree: "))

#creating an instance of the tannergraph class
tannergraph = Tannergraph(m, n, Dv)

# iterating through all variable nodes
for i in range(0, n):
    # get current variable node from tannergraph instance
    variableNode = tannergraph.variableNodes[i]
    # loop until the wanted degree of the current variable node is reached
    for k in range(0, variableNode.degree):
        # first neighbour node is chosen to be the lowest degree check node
        if k == 0:
            # find lowest degree checknode in the current tannergraph
            checkNode = tannergraph.findLowestDegreeCheckNode()
            # connect current variable node to lowest degree checknode
            tannergraph.addEdge(checkNode.index, variableNode.index)
        else:
            depth = 0
            # getSubTree() returns the subtree starting at the current variable node
            currentSubtree = tannergraph.getSubTree(depth, i)
            while(True): #change to make it more efficient !
                # condition: all checknodes are part of the current subtree
                if(currentSubtree.allCheckNodesCovered()):
                    # get subtree with decreased depth
                    previousSubtree = tannergraph.getSubTree(depth-1, i)
                    # find lowest degree check node which is not part of the subtree
                    lowestDegreeCheckNode = previousSubtree.findLowestDegreeCheckNode()
                    # connect current variable node to that check node
                    tannergraph.addEdge(lowestDegreeCheckNode.index, i)
                    break
                depth += 1
                # get subtree with increased depth
                nextSubtree = tannergraph.getSubTree(depth, i)
                # condition: cardinality of set of check at depth l stops increasing 
                if(nextSubtree.level == currentSubtree.level):
                    lowestDegreeCheckNode = currentSubtree.findLowestDegreeCheckNode()
                    tannergraph.addEdge(lowestDegreeCheckNode.index, i)
                    break
                currentSubtree = nextSubtree

print(tannergraph.Hmatrix)

file_path = 'H.mat'
scipy.io.savemat(file_path, {'tannergraph.Hmatrix' : tannergraph.Hmatrix})
np.savetxt('H1', tannergraph.Hmatrix)

H1 = tannergraph.Hmatrix

#with h5py.File('name-of-file.h5', 'w') as hf:
    #hf.create_dataset("H1",  data=H1)
f1 = h5py.File("H2048_3,6.hdf5", "w")
dset1 = f1.create_dataset("H", (1024,2048), dtype='i', data=H1)
f1.close()

