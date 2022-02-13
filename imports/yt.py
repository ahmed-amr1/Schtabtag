import urllib.request
import urllib.parse
import re
import requests
from googleapiclient.discovery import build
import orjson

with open("config.json", "r") as config:
  data = orjson.loads(config.read())
  
  YOUTUBE_API_KEY = data["youtube_api_key"]

api_key = "AIzaSyCayV6rSPPH8WqSERjUwyXYhQVcQW_YPys"

youtubeClient = build("youtube",'v3',developerKey=YOUTUBE_API_KEY)

def getData(url):
  constant = "https://www.youtube.com/watch?v="
  id = url.replace(constant,"")
  request = youtubeClient.videos().list(
    part="snippet",
    id=id
  )

  response = request.execute()

  items = response['items'][0]["snippet"]

  title = items['title']
  description = items['description']
  date = items['publishedAt']
  cover = items['thumbnails']['high']['url']
  channel = items['channelTitle']

  data = {
    'title':title,
    'description':description,
    'date':date,
    'cover':cover,
    'channel':channel
  }

  return data
  
def search(search_query):
  result = []
  html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(search_query)}")
  video_ids = re.findall(r"watch\?v=(\S{11})",html.read().decode())
  videos = []
  for id in video_ids:
    videos.append(f'https://www.youtube.com/watch?v={id}')
  for each in videos:
    data = getData(each)
    title = data['title']
    desc = data['description']
    date = data['date']
    cover = data['cover']
    channel = data['channel']

    result.append({
      "url":each,
      "title":title,
      "description":desc,
      "date":date,
      "cover":cover,
      "channel":channel
    })
  return result
