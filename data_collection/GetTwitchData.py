import requests
import json
import time
import os
from dotenv import load_dotenv
import CSVWriting
import csv

load_dotenv()
ClientID = os.getenv('ClientID')
Authorization = os.getenv('Authorization')
Headers = {'Client-ID': ClientID, 'Authorization': "Bearer " + Authorization}

#Try to call an API for time_limit seconds, if it fails return None
def make_request(url,headers=None,time_limit=90,time_sleep=2):
	start=time.time()
	failed=True
	while failed and (time.time()-start)<time_limit:
		try:
			r =requests.get(url,headers=headers) if headers!=None else requests.get(url)
			if r.status_code==200:
				failed=False
		except:
			time.sleep(time_sleep)
	return r if not failed else None

#This function return a boolean that represent if a channel is live or not
def is_live(streamer):
	r=make_request('https://api.twitch.tv/helix/streams?user_login=' + streamer, headers=Headers,time_limit= 2, time_sleep= 0.5)
	if r!=None:
		raw = r.text.encode('utf-8')
		j = json.loads(raw)
		return j['data']!=[]
	return False

#Gets the numberOfStreams top streams currently live on twitch. numberOfStreams max is 100

def GetTopStreams(numberOfStreams):
	#Header auth values taken from twitchtokengenerator.com, not sure what to do if they break
	#Request top 100 viewed streams on twitch
	r=make_request('https://api.twitch.tv/helix/streams?first=' + str(numberOfStreams)+'&language=it', headers=Headers)
	if r==None:
		raise(BaseException('Timeout getting top 100 streams'))
	raw = r.text.encode('utf-8')
	j = json.loads(raw)
	return j

#Get the a list of viewers for a given twitch channel from tmi.twitch (Not an API call)
def getCurrentViewersForChannel(channel):
	r=make_request('http://tmi.twitch.tv/group/user/'+ channel +'/chatters')
	r = r.json() if r!=None else None
	if r:#if r different from "" and None
		currentViewers = r['chatters']['vips'] + r['chatters']['viewers'] #List consists of users in chat tagged as viewer or VIP
		return currentViewers
	else:
		return None #If the query couldnt be completed return None (This occurs with foreign characters)

#This method looks up the viewers of each streamer in j and in the streamers archive (if it takes less than 120 second of execution) and creates a large dictionary of {streamer: [viewers]}
def GetDictOfStreamersAndViewers(j,max_time=120,min_rate=150):
	start=time.time()
	streamers_archive=CSVWriting.get_set_of_streamers()
	dict = {}
	writer= csv.writer(open("streamers.csv",'a+', newline=''))
	streamers = set([element['user_name'].lower() for element in j['data']]) #Get just the list of streamers
	for streamer in streamers:
		if streamer not in streamers_archive:
			writer.writerow([streamer])
		viewers = getCurrentViewersForChannel(streamer) #Get viewers for a particular streamer
		if (viewers != None):
			dict[streamer] = viewers #Add streamer to dictionary with list of viewers as value		
	#The following part of the function run only if the running time is less than max_time
	#Get viewers for other live channels saved in streamers.csv
	streamers_archive=streamers_archive-streamers
	while time.time()-start<max_time and streamers_archive!=set():
		streamer=streamers_archive.pop()
		if is_live(streamer):
			viewers = getCurrentViewersForChannel(streamer)
			if (viewers != None):
				dict[streamer] = viewers
	return dict