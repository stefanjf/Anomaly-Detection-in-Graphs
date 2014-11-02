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

files = ["datasets/enron/0_enron_by_day.txt", "datasets/enron/1_enron_by_day.txt", "datasets/enron/2_enron_by_day.txt",
         "datasets/enron/3_enron_by_day.txt", "datasets/enron/4_enron_by_day.txt"]  # glob.glob("datasets/enron/1*.txt")
sorted_files = sorted(files, key=natural_key)

# Create directed graph in networkx
pageRankNodesEdges = []

for file in sorted_files:
    f = open(file, "r")
    dataGraph = f.readlines()
    G = nx.DiGraph()

    # Add nodes to Graph object
    for line in dataGraph:
        nodeA, nodeB = line.split(" ")
        nodeA.rstrip('\r\n')
        nodeB.rstrip('\r\n')
        nodeB = nodeB[:-1]
        nodeA = int(nodeA)
        nodeB = int(nodeB)
        G.add_edge(str(nodeA), str(nodeB))

    #Add edges to pagerank object
    pr = nx.pagerank(G)
    # Iterate through edges to add to pagerank list
    for a, b in G.edges_iter():
        #print str(a) + ":" + str(b) + "  " + str(len(G.edges(a)))
        pr[str(a) + ":" + str(b)] = len(G.edges(a)) * pr[a]  #THIS NEEDS TO BE IMPROVED!!!

    #Convert every key to a md5 hash
    for key, value in pr.iteritems():
        myhash = hashlib.sha1(str(key) + str(value)).hexdigest()
        hashbinary = bin(int(myhash, 16))[2:]
        hashbinary = (hashbinary[:128]) if len(hashbinary) > 128 else hashbinary  #Trim to fixed size of 128
        pr[str(hashbinary)] = value
        del pr[key]

    pageRankNodesEdges.append(pr)

fingerprints = []
# Calculate w list
for pr in pageRankNodesEdges:
    FINAL_list = []
    for key, val in pr.iteritems():
        binary_list = []
        for d in key:
            if int(d) == 1:
                binary_list.append(val)
            else:
                binary_list.append(-val)
        FINAL_list.append(binary_list)

    file_fingerprint = [sum(x) for x in zip(*FINAL_list)]
    for index, item in enumerate(file_fingerprint):
        if item > 0:
            file_fingerprint[index] = 1
        else:
            file_fingerprint[index] = 0

    fingerprints.append(file_fingerprint)


hamming = 0.0
x=0
for x in range(len(fingerprints)-1):
    for index in range(0, 128):
        if fingerprints[x][index] != fingerprints[x+1][index]:
            hamming += 1
    print (hamming/128)



# Write out to file
f = open('community_output', 'w')
for x in output.itervalues():
    for node in x:
        f.write(str(node) + " ")
    f.write("\n")

print "Complete"
print("--- %s seconds ---" % ( time.clock() - start_time))