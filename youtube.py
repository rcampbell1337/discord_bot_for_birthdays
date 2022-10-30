import requests
from decouple import config

# Testing commit message stuff
def generate_youtube_api_url(params: list) -> str:
    """
    Generates a url for a request to the YouTube API.
    :param params: The url parameters.
    :return: The request URL.
    """
    return f"https://www.googleapis.com/youtube/v3/search?q={['%20'.join(param for param in params)]}t&maxResults=25" \
           f"&key={config('YOUTUBE_API_KEY')}"


def get_first_yt_video(birthday_person: str) -> str:
    """
    Gets a birthday youtube video for the concerned birthday person.
    :param birthday_person: The concerned birthday person.
    :return: A birthday youtube video.
    """
    youtube_video_list = requests.get(generate_youtube_api_url(
        ["HAPPY", "BIRTHDAY", f"{birthday_person.upper()}!", "-", "EPIC", "Happy", "Birthday", "Song"])).json()
    first_video_id = youtube_video_list["items"][0]["id"]["videoId"]
    return f"https://www.youtube.com/watch?v={first_video_id}"