import sys
import time
import glob
import re
import networkx as nx

def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

start_time = time.clock()

files = glob.glob("datasets/enron/*.txt")
sorted_files = sorted(files, key=natural_key)

#Create directed graph in networkx
arrayOfGraphs = []
arrayOfPR = []
for file in sorted_files:
    f = open(file, "r")
    dataGraph = f.readlines()
    G = nx.DiGraph()

    for line in dataGraph:
        nodeA, nodeB = line.split(" ")
        nodeA.rstrip('\r\n')
        nodeB.rstrip('\r\n')
        nodeB = nodeB[:-1]
        nodeA = int(nodeA)
        nodeB = int(nodeB)

        G.add_edge(nodeA, nodeB)

    pr = nx.pagerank(G)
    arrayOfGraphs.append(G)
    arrayOfPR.append(pr)

#Define data structures
Array_Of_Adj_Lists = []

for file in files:
    f = open(file, "r")
    dataGraph = f.readlines()
    adjacency_List = []

    for line in dataGraph:
        nodeA, nodeB = line.split(" ")
        nodeA.rstrip('\r\n')
        nodeB.rstrip('\r\n')
        nodeB = nodeB[:-1]
        nodeA = int(nodeA)
        nodeB = int(nodeB)

        adjacency_List.append([nodeA, nodeB])

    Array_Of_Adj_Lists.append(adjacency_List)


print Array_Of_Adj_Lists

#Calculate Quality Scores






#Write out to file
f = open('community_output', 'w')
for x in output.itervalues():
    for node in x:
        f.write(str(node) + " ")
    f.write("\n")

print "Complete"
print("--- %s seconds ---" %( time.clock() - start_time))