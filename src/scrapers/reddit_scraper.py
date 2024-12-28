import os
import json
import datetime
from dotenv import load_dotenv
import praw


def init_reddit_client():
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    password = os.getenv("REDDIT_PASSWORD")
    user_agent = os.getenv("REDDIT_USER_AGENT")
    username = os.getenv("REDDIT_USERNAME")

    if not client_id or not client_secret or not user_agent:
        raise ValueError("Reddit API credentials are missing")

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        password=password,
        user_agent=user_agent,
        username=username,
    )


def scrape_subreddit(subreddit_name, sort_by="hot", limit=10):
    reddit = init_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)

    posts = []
    if sort_by == "hot":
        submissions = subreddit.hot(limit=limit)
    elif sort_by == "new":
        submissions = subreddit.new(limit=limit)
    elif sort_by == "top":
        submissions = subreddit.top(limit=limit)
    else:
        raise ValueError("Invalid sort_by value. Choose from 'hot', 'new', or 'top'.")

    for submission in submissions:
        posts.append(
            {
                "title": submission.title,
                "url": submission.url,
                "score": submission.score,
                "comments": submission.num_comments,
                "created_utc": submission.created_utc,
            }
        )

    return posts


def download_post(post_url, output_path="data/scraped_data/posts"):
    reddit = init_reddit_client()
    submission = reddit.submission(url=post_url)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    utc_now = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S")
    filename = f"{utc_now}.json"

    data = {
        "post_url": post_url,
        "title": submission.title,
        "text_content": submission.selftext,
        "score": submission.score,
        "num_comments": submission.num_comments,
        "created_utc": submission.created_utc,
        "downloaded_at": utc_now,
    }

    file_path = os.path.join(output_path, filename)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Post downloaded to: {file_path}")
    return file_path


if __name__ == "__main__":
    load_dotenv()

    subreddit_name = "AmItheAsshole"
    print(f"Scraping {subreddit_name} subreddit...")

    posts = scrape_subreddit(subreddit_name, sort_by="hot", limit=10)
    for i, post in enumerate(posts):
        print(
            f"{i + 1}. {post['title']} (Score: {post['score']}, Comments: {post['comments']})"
        )
        print(f"URL: {post['url']}")
        print()
