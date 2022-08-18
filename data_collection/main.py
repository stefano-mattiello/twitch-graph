import GetTwitchData
import CSVWriting
import time
import csv
import json
import os
#os.chdir('path')
#This function get the data from Twitch and then update the csv file data.csv
def update_csv():
	now=int(time.time())
	#Read the data
	with open('data.json', 'r') as f:
		old_data = json.load(f)
	#Get the top 100 streams on Twitch
	j = GetTwitchData.GetTopStreams(100)
	if j==None:
		return
	#Create a dictionary of {streamer:[viewers]} from those 100 streams
	current_data= GetTwitchData.GetDictOfStreamersAndViewers(j) 
	#Update the dictionary d with the obtained data 
	new_data,n_users=CSVWriting.updatedict(old_data,current_data,now)

	#Save the updated data
	with open('data.json', 'w') as json_file:
		json.dump(new_data, json_file)
	
	#Save the number of users at this time
	row=[now,n_users]
	
	with open("users.csv", 'a+', newline='') as write_obj:
		csv_writer = csv.writer(write_obj)
		csv_writer.writerow(row)


class main():
	update_csv()      #Collect the data and update the file
		




