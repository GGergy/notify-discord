import yandex_music
import requests
from bs4 import BeautifulSoup
from .yt_api import get_title
from .config import music_key


conn = yandex_music.Client(token=music_key)
conn.init()


def search(query):
    tracks_id = parse_link(query)
    if tracks_id:
        return [{"id": track_id, "name": get_metadata(track_id)} for track_id in tracks_id]
    response = []
    answer = conn.search(text=query, type_='all')
    if not answer.tracks:
        return []
    for item in answer.tracks.results[:25]:
        if isinstance(item.id, int):
            response.append({"id": item.id, "name": f'{item.title} - {", ".join([i.name for i in item.artists])}'[:80]})
    return response


def get_link(track_id):
    return conn.tracks_download_info(track_id=track_id, get_direct_links=True)[0].direct_link


def get_metadata(track_id):
    if not str(track_id).isdigit():
        if '.mp3' not in str(track_id):
            return get_title(f"https://www.youtube.com/watch?v={track_id}")
        else:
            return track_id
    track = conn.tracks([track_id])[0]
    return f'{track.title} - {", ".join([i.name for i in track.artists])}'


def parse_link(link):
    if not link.startswith('https://music.yandex.ru/'):
        return False
    if link.startswith('https://music.yandex.ru/album/') and 'track' in link:
        try:
            re = link.split('/')[6]
            return [int(re[:re.index('?')])]
        except Exception:
            pass
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        ids = soup.find_all(lambda tag: tag.get('class') and 'd-track' in tag.get('class'))
        return [int(item.get('data-item-id')) for item in ids][:25]
    except Exception as e:
        print('link parse failed', e)
        return False
