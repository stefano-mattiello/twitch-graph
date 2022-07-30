import GetTwitchData
import CSVWriting
import os
import sys
import datetime
import csv

#This function get the data from Twitch andd then update the csv file data.csv
def update_csv():
	
	
	now = datetime.datetime.now()
	row=["%4.f %2.f %2.f %2.f %2.f"%(now.year, now.month, now.day, now.hour, now.minute)]
	
	#Read the data
	old_data=CSVWriting.readcsv()
	
	
	#Get the top 100 streams on Twitch
	json = GetTwitchData.GetTopStreams(3) 
	#Create a dictionary of {streamer:[viewers]} from those 100 streams
	current_data = GetTwitchData.GetDictOfStreamersAndViewers(json) 
	
	#Update the dictionary d with the obtained data 
	new_data,n_users=CSVWriting.updatedict(old_data,current_data)

	#Save the updated data
	CSVWriting.writecsv(new_data)
	
	
	#Save the number of users at this time
	row.append(n_users)
	
	with open("users.csv", 'a+', newline='') as write_obj:
         	csv_writer = csv.writer(write_obj)
         	csv_writer.writerow(row)


class main():
	update_csv()      #Collect the data and update the file
		




