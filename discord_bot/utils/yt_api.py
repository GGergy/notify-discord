import os.path
import shutil
import requests
from pytube import YouTube, Playlist
import re

try:
    shutil.rmtree('temp')
except:
    pass

os.mkdir('temp')


def match(arr: list) -> list:
    response = []
    for item in arr:
        if len(response) >= 10:
            break
        if item not in response:
            response.append(item)
    return response


def search(query):
    if query.startswith("https://www.youtube.com/watch"):
        return [{"name": query, "id": query[query.rfind('/') + 9:]}]
    if query.startswith("https://www.youtube.com/playlist"):
        playlist = Playlist(url=query).videos
        watches = [video.watch_url for video in playlist]
        return [{"name": w, "id": w[w.rfind('v=') + 2:]} for w in watches]
    resp = requests.get(f"https://www.youtube.com/results", params={"search_query": query})
    video_ids = match(re.findall(r"watch\?v=(\S{11})", resp.text))
    video_ids = [{"name": f"https://www.youtube.com/watch?v={vid}",
                  "id": vid} for vid in video_ids]
    return video_ids


def get_link(vid):
    if os.path.isfile(f'temp/{vid}.mp4'):
        return os.path.join(os.path.abspath('.'), 'temp', f'{vid}.mp4')
    a = YouTube(f"https://www.youtube.com/watch?v={vid}").streams.filter(only_audio=True,
                                                                         file_extension='mp4')[-1].\
        download(output_path='temp', filename=f'{vid}.mp4')
    return a
