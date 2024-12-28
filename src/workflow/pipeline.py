import json
from dotenv import load_dotenv
from scrapers.youtube_scraper import search_youtube, download_video
from scrapers.reddit_scraper import scrape_subreddit, download_post

load_dotenv()


def run_scrape_pipeline():
    print("Step 1: Scraping Reddit for content ideas...")
    subreddit_name = "AmItheAsshole"
    reddit_posts = scrape_subreddit(subreddit_name, sort_by="hot", limit=5)

    print(f"Found {len(reddit_posts)} posts from r/{subreddit_name}:")
    downloaded_reddit_posts = []
    for i, post in enumerate(reddit_posts):
        print(
            f"{i + 1}. {post['title']} (Score: {post['score']}, Comments: {post['comments']})"
        )
        print(f"URL: {post['url']}")
        print()

        try:
            post_file = download_post(post["url"])
            print(f"Reddit post downloaded to: {post_file}")
            downloaded_reddit_posts.append(post_file)
        except Exception as e:
            print(f"Failed to download Reddit post: {e}")

    print("Step 2: Searching YouTube for related videos...")
    query = "minecraft parkour gameplay no copyright 4k"
    youtube_videos = search_youtube(query, max_results=5)

    print(f"Found {len(youtube_videos)} videos on YouTube:")
    downloaded_youtube_videos = []
    for i, video in enumerate(youtube_videos):
        print(f"{i + 1}. {video['title']} by {video['channel']} ({video['link']})")
    print()

    if youtube_videos:
        print("Step 3: Downloading the top YouTube video...")
        try:
            top_video = youtube_videos[0]
            output_path = "data/scraped_data/videos"
            downloaded_file = download_video(top_video["link"], output_path)
            print(f"Video downloaded to: {downloaded_file}")
            downloaded_youtube_videos.append(downloaded_file)
        except Exception as e:
            print(f"Failed to download YouTube video: {e}")
    else:
        print("No videos found to download.")

    print("Step 4: Combining scraped content for processing...")
    combined_data = {
        "reddit_posts": reddit_posts,
        "downloaded_reddit_posts": downloaded_reddit_posts,
        "youtube_videos": youtube_videos,
        "downloaded_youtube_videos": downloaded_youtube_videos,
    }

    output_path = "data/scraped_data/combined_data.json"
    try:
        with open(output_path, "w") as f:
            json.dump(combined_data, f, indent=4)
        print(f"Combined data saved to: {output_path}")
    except Exception as e:
        print(f"Failed to save combined data: {e}")

    print("Pipeline completed.")
    return combined_data


if __name__ == "__main__":
    pipeline_data = run_scrape_pipeline()
    print("\nPipeline Data:")
    print(json.dumps(pipeline_data, indent=4))
