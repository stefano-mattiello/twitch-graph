import csv
import sys
import pandas as pd
import numpy as np
import os
import time

def updatedict(dict0,dict1):

	n_users=0
	set_users=set()
	for streamer in dict1.keys():
		streamer_dict=dict0.setdefault(streamer,{'streaming':0})
		streamer_dict['streaming']+=1
		for user in dict1[streamer]:
			if user not in set_users:
				n_users+=1
				set_users.add(user)
			user_dict=dict0.setdefault(user,{'streaming':0})
			user_dict[streamer]=user_dict.setdefault(streamer,0)+1
	return dict0,n_users

def readcsv():
    reader = csv.reader(open("data.csv"))

    users_dict={}
    for row in reader:
        user=row[0]
        users_dict[user]={}
        for i in range(1,(len(row)-1),2):
            users_dict[user][row[i]]=int(row[i+1])
    return users_dict


def writecsv(users_dict):
    writer= csv.writer(open("data.csv",'w'))
    for user,user_dict in users_dict.items():
        row=[]
        for streamer,count in user_dict.items():
            row+=[streamer,count]
        writer.writerow([user]+row)



