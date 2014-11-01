import sys
import time
import glob
import re
import networkx as nx
import hashlib


def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


start_time = time.clock()

files = glob.glob("datasets/enron/*.txt")
sorted_files = sorted(files, key=natural_key)

# Create directed graph in networkx
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
    #Iterate through edges to add to pagerank list
    for a, b in G.edges_iter():
        print str(a) + ":" + str(b) + "  " + str(len(G.edges(a)))
        pr[str(a) + ":" + str(b)] = len(G.edges(a)) * pr[a]  #THIS NEEDS TO BE IMPROVED!!!
        myhash = hashlib.md5(str(a) + str(b)).hexdigest()
        hashbinary = bin(int(myhash, 16))[2:]
        print hashbinary

    binary_list = []
    for d in hashbinary:
        if d == 1:
            binary_list.append(pr[])
        else:
            binary_list.append()

    arrayOfGraphs.append(G)
    arrayOfPR.append(pr)

#Calculate Quality Scores
print arrayOfPR






#Write out to file
f = open('community_output', 'w')
for x in output.itervalues():
    for node in x:
        f.write(str(node) + " ")
    f.write("\n")

print "Complete"
print("--- %s seconds ---" % ( time.clock() - start_time))