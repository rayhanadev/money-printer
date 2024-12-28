import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from pytubefix import YouTube
import datetime


def init_youtube_client():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing")

    return build("youtube", "v3", developerKey=api_key)


def search_youtube(query, max_results=10):
    youtube = init_youtube_client()
    request = youtube.search().list(
        part="snippet", q=query, type="video", maxResults=max_results
    )
    response = request.execute()

    videos = []
    for item in response["items"]:
        videos.append(
            {
                "title": item["snippet"]["title"],
                "link": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "channel": item["snippet"]["channelTitle"],
                "published_at": item["snippet"]["publishedAt"],
            }
        )
    return videos


def download_video(video_url, output_path="data/scraped_data/videos"):
    yt = YouTube(video_url)
    ys = yt.streams.get_highest_resolution(progressive=False)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    downloaded_file = ys.download(output_path=output_path)

    utc_now = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S")
    extname = os.path.splitext(downloaded_file)[1]
    new_filename = f"{utc_now}{extname}"

    new_file_path = os.path.join(output_path, new_filename)
    os.rename(downloaded_file, new_file_path)

    return f"{output_path}/{new_filename}"


if __name__ == "__main__":
    load_dotenv()

    query = "minecraft parkour gameplay no copyright 4k"
    print(f"Searching for: {query}")

    results = search_youtube(query)
    for i, video in enumerate(results):
        print(f"{i + 1}. {video['title']} ({video['link']})")

    first_video_url = results[0]["link"]
    print(f"Downloading: {first_video_url}")
    download_path = download_video(first_video_url)
    print(f"Downloaded to: {download_path}")
