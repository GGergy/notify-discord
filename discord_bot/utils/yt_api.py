import requests
from pytube import YouTube, Playlist
from functools import lru_cache
import re


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
        title = get_title(query)
        if not title:
            return []
        return [{"name": title, "id": query[query.rfind('/') + 9:]}]
    elif query.startswith("https://www.youtube.com/playlist"):
        playlist = Playlist(url=query).videos
        watches = [video.watch_url for video in playlist]
        return [{"name": get_title(w), "id": w[w.rfind('v=') + 2:]} for w in watches if get_title(w)]
    resp = requests.get(f"https://www.youtube.com/results", params={"search_query": query})
    video_ids = match(re.findall(r"watch\?v=(\S{11})", resp.text))
    video_ids = [{"name": get_title(f"https://www.youtube.com/watch?v={vid}"),
                  "id": vid} for vid in video_ids if get_title(f"https://www.youtube.com/watch?v={vid}")]
    return video_ids


def get_link(vid):
    yt = YouTube(f"https://www.youtube.com/watch?v={vid}")
    return yt.streams.filter(only_audio=True).get_audio_only().url


@lru_cache
def get_title(vid):
    yt = YouTube(vid)
    if yt.age_restricted:
        return False
    return f'{yt.author} - {yt.title}'[:80]
