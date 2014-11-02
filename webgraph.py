import glob
import re
import hashlib
import networkx as nx
import time
import numpy


#This function was copied from http://stackoverflow.com/questions/2545532/python-analog-of-natsort-function-sort-a-list-using-a-natural-order-algorithm
#It allows for natural sorting for the input files
def natural_key(string_):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

start_time = time.clock()

#Load dataset
# files = ["datasets/enron/0_enron_by_day.txt", "datasets/enron/1_enron_by_day.txt", "datasets/enron/2_enron_by_day.txt",
# "datasets/enron/3_enron_by_day.txt", "datasets/enron/4_enron_by_day.txt"]  #
files = glob.glob("datasets/enron/*.txt")
sorted_files = sorted(files, key=natural_key)

# Create directed graph in networkx
list_All_Feature_Set = []

#Loop through each graph file
for file in sorted_files:
    f = open(file, "r")
    dataGraph = f.readlines()

    #Create networkx graph object
    G = nx.DiGraph()

    # Add edges to Graph object from input file
    for line in dataGraph:
        nodeA, nodeB = line.split(" ")
        G.add_edge(str(nodeA), str(nodeB))

    #Generate dictionary with pagerank (quality) values for each node
    weighted_Feature_Set = nx.pagerank(G)

    #Add edge "quality" from graph to weighted feature set
    for a, b in G.edges_iter():
        weighted_Feature_Set[str(a) + " " + str(b)] = len(G.edges(a)) * weighted_Feature_Set[a]
    #THIS NEEDS TO BE IMPROVED!!!

    #Convert every key to a md5 hash
    for key, value in weighted_Feature_Set.items():
        sha1_hash = hashlib.sha1(str(key) + str(value)).hexdigest()
        binary_hash = bin(int(sha1_hash, 16))[2:]
        #Trim to fixed size of 128
        binary_hash = (binary_hash[:128]) if len(binary_hash) > 128 else binary_hash
        #Add sha1 hash with corresponding value to feature set
        weighted_Feature_Set[str(binary_hash)] = value
        #Remove original key/value from feature set
        del weighted_Feature_Set[key]

    #Add file
    list_All_Feature_Set.append(weighted_Feature_Set)

    print "Processed file: " + file

#List of all document fingerprints
all_Fingerprints = []

#Loop through each feature set to generate it's fingerprint
for feature_Set in list_All_Feature_Set:
    temp_fingerprint = []
    #Build fingerprint
    for key, val in feature_Set.iteritems():
        binary_list = []
        #For each sha1 hash, if digit=1 then add weighted value. If digit=0, then add negative weighted value.
        for d in key:
            if int(d) == 1:
                binary_list.append(val)
            else:
                binary_list.append(-val)
        temp_fingerprint.append(binary_list)

    #Calculate fingerprint by summing all the columns in temp_fingerprint
    fingerprint = [sum(x) for x in zip(*temp_fingerprint)]

    #Convert all positive vals to '1' and all negative vals to '0' in fingerprint
    for index, item in enumerate(fingerprint):
        if item > 0:
            fingerprint[index] = 1
        else:
            fingerprint[index] = 0

    #Add fingerprint to list
    all_Fingerprints.append(fingerprint)


###Post Processing###
hamming_Results = []
#Calculate hamming distance between each sequential pair of fingerprints
x = 0
for x in range(len(all_Fingerprints) - 1):
    hamming = 0.0
    #Calculate hamming distance
    for index in range(0, 128):
        if all_Fingerprints[x][index] == all_Fingerprints[x + 1][index]:
            hamming += 1
    hamming_Results.append(1-(hamming/128))
    print (1-(hamming / 128))

#Calculate median
median = numpy.median(numpy.array(hamming_Results))
print "Median Value: " + str(median)

#Moving Range
movingRangeAvg = []
tempAvgNumerator = 0
print "Moving Average:"
for y in range(len(hamming_Results)-1):
    #Add 1 to y so it starts at the second value (first pair)
    if y == 0:
        tempAvgNumerator = abs(hamming_Results[y+1]-hamming_Results[y])
    else:
        tempAvgNumerator = tempAvgNumerator + abs(hamming_Results[y+1]-hamming_Results[y])

    average = median + tempAvgNumerator/(y+1)
    print average
    movingRangeAvg.append(average)
#print movingRangeAvg


print "Complete"
print("--- %s seconds ---" % ( time.clock() - start_time))