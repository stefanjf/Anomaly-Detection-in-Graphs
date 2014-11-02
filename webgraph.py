import glob
import re
import hashlib
import networkx as nx
import time
import numpy
import operator
import math

#This function was copied from http://stackoverflow.com/questions/2545532/python-analog-of-natsort-function-sort-a-list-using-a-natural-order-algorithm
#It allows for natural sorting for the input files, so they're read in the correct order
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
        nodeA.rstrip('\r\n')
        nodeB.rstrip('\r\n')
        nodeB = nodeB[:-1]
        G.add_edge(str(nodeA), str(nodeB))

    #Generate dictionary with pagerank (quality) values for each node
    weighted_Feature_Set = nx.pagerank(G)

    #Add edge "quality" from graph to weighted feature set
    for a, b in G.edges_iter():
        weighted_Feature_Set[str(a) + " " + str(b)] = (1/len(G.edges(a))) * weighted_Feature_Set[a]
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
similarity_scores = []
#Calculate hamming distance between each sequential pair of fingerprints
x = 0
for x in range(len(all_Fingerprints) - 1):
    hamming = 0.0
    #Calculate hamming distance
    for index in range(0, 128):
        if all_Fingerprints[x][index] == all_Fingerprints[x + 1][index]:
            hamming += 1
    similarity_scores.append(1-(hamming/128))
    #print "Similarity score between " + str(x) + " and " + str(x+1) + " : " + str(1-(hamming / 128))

#Calculate median
median = numpy.median(numpy.array(similarity_scores))
print "Median Value: " + str(median)

#Moving Range
thresholdList = []
tempAvgNumerator = 0
multiplierForMR = 1
#print "Moving Average:"
for y in range(len(similarity_scores)-1):
    #Add 1 to y so it starts at the second value (first pair)
    if y == 0:
        tempAvgNumerator = 0
        #print "MR for time point " + str(y) + ": N/A"
    else:
        tempAvgNumerator = tempAvgNumerator + abs(similarity_scores[y+1]-similarity_scores[y])
        threshold = median - (multiplierForMR*tempAvgNumerator/(y+1))
        thresholdList.append(threshold)
        #print threshold

#Detect anomalies
anomalies = {}
for x in range(len(similarity_scores)):
    if x > 1: #No moving average to compare for the first graph
        #Detect two consecutive anomalies
        if (similarity_scores[x] < thresholdList[x-2]) and (similarity_scores[x+1] < thresholdList[x-1]):
            anomalies[str(x+2)] = abs(similarity_scores[x] - thresholdList[x-2]) + abs(similarity_scores[x+1] - thresholdList[x-1])

###Output Anomalies###
#You will list all of the anomalous time points if
#there are fewer than 10, the top 10 if there are fewer than 100, or the top 10% if there are
#more than 100.
f = open('anomalies_output', 'w')
sorted_anomalies = sorted(anomalies.items(), key=operator.itemgetter(1), reverse=True)
numOfAnomalies = len(sorted_anomalies)
if numOfAnomalies > 100:
    print "There are more than 100 anomalies detected, so we will output the top 10%"
    for x in range(math.ceil(0.1*len(numOfAnomalies))):
        f.write(str(sorted_anomalies[x][0]))
        f.write("\n")
elif numOfAnomalies < 11:
    print "There are fewer than 100 anomalies detected, so we will output the top 10"
    for x in numOfAnomalies:
        f.write(str(sorted_anomalies[x][0]))
        f.write("\n")
else:
    print "There are fewer than 10 anomalies detected, so we will output all of them"
    for x in range(0,10):
        f.write(str(sorted_anomalies[x][0]))
        f.write("\n")
f.close()

print "Complete"
print("--- %s seconds ---" % ( time.clock() - start_time))

print "Writing out to file."
#Write out to file
f = open('sim_score_output', 'w')
for x in similarity_scores:
    f.write(str(x))
    f.write("\n")
f.close()

f = open('moving_thresholds', 'w')
for x in thresholdList:
    f.write(str(x))
    f.write("\n")
f.close()