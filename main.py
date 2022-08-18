# -*- coding: UTF-8 -*-
import os
import json
import time
from dotenv import load_dotenv
import tweepy
import spotipy
from spotipy_random import get_random
from spotipy.oauth2 import SpotifyClientCredentials
from moviepy.editor import ImageClip, AudioFileClip
from apscheduler.schedulers.blocking import BlockingScheduler

# Some setup stuff for Twitter API
load_dotenv()
auth = tweepy.OAuthHandler(os.getenv('CONSUMER_KEY'), os.getenv('CONSUMER_SECRET'))
auth.set_access_token(os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET'))
api = tweepy.API(auth)

# Some setup stuff for Spotify API
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def make_tweet():
    print(bcolors.OKGREEN + "Starting Job" + bcolors.ENDC)
    data = get_random(spotify, type="track", offset_min=1, offset_max=1000)
    if data is None:
        print(bcolors.FAIL + "No data found" + bcolors.ENDC)
        return make_tweet()
    jsonString = json.dumps(data)
    result = json.loads(jsonString)
    formatted = json.dumps(result, indent=2, sort_keys=True)
    time.sleep(5)
    # print(formatted)
    print(bcolors.OKGREEN + "Fetch from Spotify done" + bcolors.ENDC)

    # Setup the data to be tweeted
    songName = result['name']
    songArtist = result['artists'][0]['name']
    songImageUrl = result['album']['images'][0]['url']
    songPreviewUrl = result['preview_url']
    songUrl = result.get('external_urls').get('spotify')

    if songPreviewUrl is None:
        print(bcolors.FAIL + "No preview available\nJob Failed" + bcolors.ENDC)
        return make_tweet()

    # Create the video
    fileName = songName + '_' + songArtist + '.mp4'
    videoSample = ImageClip(songImageUrl)
    audioSample = AudioFileClip(songPreviewUrl)
    videoSample = videoSample.set_audio(audioSample)
    videoSample.duration = audioSample.duration
    videoSample.fps = 30
    videoSample.write_videofile(fileName, audio_codec='aac', codec='libx264')
    print(bcolors.OKGREEN + "Video Created" + bcolors.ENDC)

    # Post final tweet
    Tweet = '📢 NEW DISCOVERY OF THE HOUR 📢\n\n'
    Tweet += '🎵 ' + songName + ' by ' + songArtist + ' 🎵\n\n' + songUrl

    time.sleep(5)
    uploadResult = api.media_upload(filename=fileName)
    api.update_status(Tweet, media_ids=[uploadResult.media_id])
    print(bcolors.OKGREEN + "Tweet Posted" + bcolors.ENDC)
    os.remove(fileName)

    # Cleanup stuff
    del data
    del jsonString
    del result
    del formatted
    del songName
    del songArtist
    del songImageUrl
    del songPreviewUrl
    del songUrl
    del fileName
    del videoSample
    del audioSample
    del Tweet
    del uploadResult
    print(bcolors.OKGREEN + "Cleanup Done" + bcolors.ENDC)
    print(bcolors.OKGREEN + "Job Done\n" + bcolors.ENDC)

scheduler = BlockingScheduler()
scheduler.add_job(make_tweet, 'interval', minutes=1)
scheduler.start()