import sys
import csv
import CSVWriting
import json

#This function take a dictionary {user_1: {streamer_1:[time_1,..,time_l],streamer_2:[time_1,..,time_c]},...}
#and returns {user_1: {streamer_1:l,streamer_2:c},...}
#
def flatten_dict(d):
    new_d=dict()
    for user in d.keys():
        new_d[user]=dict()
        for streamer in d[user].keys():
            if streamer!='streaming':
                new_d[user][streamer]=len(d[user][streamer])
    return new_d
    

#This function removes:
#	the users that have been detected too many times (since they are probably bots) 
#	the users that have watched a streamer less than 2 hours 
def filter_dict(old_dict,max_count=900,min_count=8):
    newdict=dict()
    userlist=[user for user in old_dict.keys() if sum(old_dict[user].values())<max_count]
    for user in userlist:
        for streamer in old_dict[user].keys():
                if old_dict[user][streamer]>=min_count:
                    user_dict=newdict.setdefault(user,dict())
                    user_dict[streamer]=old_dict[user][streamer]
    return newdict


#This function returns a dictionary {streamer: [...users]}
def getrawdict(old_dict):
	newdict={}
	for user,userdict in old_dict.items():
		for streamer in userdict:
			if streamer!='streaming':
				streamercomm=newdict.setdefault(streamer,[])
				streamercomm.append(user)
	return newdict
		

#This is the main analysis function for the data.
#It creates a dictionary of the form {streamer1: {streamer2: overlap, streamer3: overlap}}
#This allows us to have an integer of overlapping viewers for each streamer with every other streamer
def CreateOverlapDict(dict,min_overlap=40):
    viewerOverlapDict = {}
    count = 1
    completedStreamers = set() #Save which streamers have been processed to avoid repeating
    for key in dict:
        dict[key] = set(dict[key]) #Make viewer list a set to dramatically decrease comparison time
    totalLength = len(dict.keys())
    for key in dict:
        tempList = {}
        print(str(count) + "/" + str(totalLength)) #Print progress so I can keep track
        if len(dict[key])>min_overlap:
            for comparisonKey in dict: #Loop through every key again for each key in the dictionary
                if(comparisonKey != key and comparisonKey not in completedStreamers): #If its not a self comparison and the comparison hasn't already been completed
                    overlapSize = len(dict[key] & dict[comparisonKey]) #Find the overlap size of the two streamers using set intersection
                    if(overlapSize > min_overlap ):
                        tempList[comparisonKey] = overlapSize #If the size is over min_overlap add {comparisonStreamer: overlap} to the dictionary
            viewerOverlapDict[key] = tempList #Add this comparison dictionary to the larger dictionary for that streamer
            completedStreamers.add(key) #Add the streamer to completed as no comparisons using this streamer need to be done anymore
        count+=1
    return viewerOverlapDict



def GenerateGephiData(dict,rawdict,path):
    print("Generating Data...")
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        #writer.writeheader()
        writer.writerow(["Source", "Target", "Weight","Shared viewers"]) #These column headers are used in Gephi automatically
        for key, value in dict.items():
            nodeA = key
            for node, count in value.items():
                nodeB = node
                weight=count/min(len(rawdict[nodeA]),len(rawdict[nodeB]))
                if weight>=0.1:
                	writer.writerow([nodeA, nodeB, weight ,count]) #nodeA is streamer1, nodeB is streamer2, and count is their overlapping viewers

#Generates a new csv file for the node list labels on Gephi
def GenerateGephiLabels(rawDict,path,path_data):
    print("Generating Labels...")
    sys.stdout.flush()
    #Since we are not interested in nodes without any edge, we create a set of nodes and then calculate their weight
    streamers=set() 
    reader = csv.reader(open(path_data))
    for row in reader:
        streamers.add(row[0])
        streamers.add(row[1])
        
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Label", "Unique viewers"]) #These columns are used in Gephi automatically
        
        for key, value in rawDict.items():
                if key in streamers:
                       writer.writerow([key, key, len(value)]) #This data is streamer1, streamer1, and # of unique viewers for streamer1
#Generate Gephi data files with the dictionaries

class main():
	#Read the data from the csv
    with open('data.json', 'r') as f:
        d = json.load(f)
    #Keep only the number of detection
    d=flatten_dict(d)
	#Remove users with too many or too little detections
    filtered_dict=filter_dict(d,1400,3)
	#Get dictionary  {streamer: [...users]} of the communities
    rawDict = getrawdict(filtered_dict) 
	#Process data creating dictionary of {streamer1: {streamer2: overlap, streamer3: overlap}}
    dict1= CreateOverlapDict(rawDict) 
	#Generate data for Gephi
    path_data,path_labels='test_data.csv','test_label.csv'
    GenerateGephiData(dict1,rawDict,path_data)
    GenerateGephiLabels(rawDict,path_labels,path_data)
