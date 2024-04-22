'''Twitter Module'''
from datetime import timedelta
from http import HTTPStatus
import requests

from exceptions import NoVideoFoundError

URL_JSON = 'https://cdn.syndication.twimg.com/tweet-result'
TIMEOUT = timedelta(minutes=5).seconds

def get_twitter_id(url: str):
    '''Get the id of the tweet'''
    part = url.split('/')[-1]
    return int(part.split('?')[0])

def get_twitter_video(url: str):
    '''Get the video from the tweet'''
    id = get_twitter_id(url)
    params = {
        'id': id,
        'token': "SAjfdshj3"
    }

    res_json = requests.get(URL_JSON, params=params, timeout=TIMEOUT)

    if res_json.status_code != HTTPStatus.OK:
        raise ConnectionError(f'Error {res_json.status_code}: could scrape the video')

    content = res_json.json()
    media_details = content['mediaDetails'][0]
    if 'video_info' not in media_details:
        raise NoVideoFoundError('No video found in the tweet')

    bitrate = 0
    video_url = ''
    for video in media_details['video_info']['variants']:
        if 'bitrate' in video:
            if video['bitrate'] > bitrate:
                bitrate:int = video['bitrate']
                video_url:str = video['url']

    res_video = requests.get(video_url, timeout=TIMEOUT)

    return res_video.content
