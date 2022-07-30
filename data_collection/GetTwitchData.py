import requests
import json
import sys
import io
import os
from dotenv import load_dotenv

load_dotenv()

ClientID = os.getenv('ClientID')
Authorization = os.getenv('Authorization')

#Gets the numberOfStreams top streams currently live on twitch. numberOfStreams max is 100

def GetTopStreams(numberOfStreams):

	#Header auth values taken from twitchtokengenerator.com, not sure what to do if they break
	Headers = {'Client-ID': ClientID, 'Authorization': "Bearer " + Authorization}

	#Request top 100 viewed streams on twitch
	r = requests.get('https://api.twitch.tv/helix/streams?first=' + str(numberOfStreams)+'&language=it', headers=Headers)
	raw = r.text.encode('utf-8')
	j = json.loads(raw)
	return j

#Get the a list of viewers for a given twitch channel from tmi.twitch (Not an API call)
def getCurrentViewersForChannel(channel):

	r = requests.get('http://tmi.twitch.tv/group/user/'+ channel.lower() +'/chatters').json()
	if(r != ""):
		currentViewers = r['chatters']['vips'] + r['chatters']['viewers'] #List consists of users in chat tagged as viewer or VIP
		return currentViewers
	else:
		return None #If the query couldnt be completed return None (This occurs with foreign characters)

#This method looks up the viewers of each streamer in j and creates a large dictionary of {streamer: [viewers]}
def GetDictOfStreamersAndViewers(j):

	dict = {}
	streamers = [element['user_name'] for element in j['data']] #Get just the list of streamers
	for streamer in streamers:
		streamer_lower=streamer.lower()
		viewers = getCurrentViewersForChannel(streamer_lower) #Get viewers for a particular streamer
		if (viewers != None):
			dict[streamer_lower] = viewers #Add streamer to dictionary with list of viewers as value		
	return dict
