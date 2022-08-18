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

#Gets the numberOfStreams top streams currently live on twitch. numberOfStreams max is 100

def GetTopStreams(numberOfStreams,cursor=None):
	#Header auth values taken from twitchtokengenerator.com, not sure what to do if they break
	#Request top 100 viewed streams on twitch
	r=make_request('https://api.twitch.tv/helix/streams?first=' + str(numberOfStreams)+'&language=it', headers=Headers) if cursor==None else make_request('https://api.twitch.tv/helix/streams?first=' + str(numberOfStreams)+'&language=it'+'&after='+cursor, headers=Headers)
	if r!=None:
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
def GetDictOfStreamersAndViewers(j,max_time=120):
	start=time.time()
	dict = {}
	for stream in j['data']:
		streamer_name=stream['user_name'].lower()
		viewers = getCurrentViewersForChannel(streamer_name) #Get viewers for a particular streamer
		if (viewers != None):
			dict[streamer_name] = {'viewers':viewers,'stream_info':{'game_name':stream['game_name'],'viewer_count':stream['viewer_count'],'is_mature':stream['is_mature']}} #Add streamer to dictionary with list of viewers as value		
	last=True
	#The following part of the function run only if the running time is less than max_time
	#It continues to request streams until it tuns out of time or there are no more streams to get (or the API request fails)
	while time.time()-start<max_time:
		if last:
			last=False
			i=0
			cursor=j['pagination']['cursor']
			j=GetTopStreams(100,cursor=cursor)
			if j==None:
				return dict
			length=len(j['data'])
			if length==0:
				return dict
		stream=j['data'][i]
		streamer_name=stream['user_name'].lower()
		viewers = getCurrentViewersForChannel(streamer_name)
		if (viewers != None):
			dict[streamer_name] = {'viewers':viewers,'stream_info':{'game_name':stream['game_name'],'viewer_count':stream['viewer_count'],'is_mature':stream['is_mature'],'tag_ids':stream['tag_ids']}}
		i+=1
		if i==length:
			last=True
	return dict