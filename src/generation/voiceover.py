from dotenv import load_dotenv
import os
import openai
import json
import textwrap


def load_pipeline_data(filepath="data/scraped_data/combined_data.json"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Pipeline data file not found: {filepath}")

    with open(filepath, "r") as f:
        data = json.load(f)

    return data


def select_story(pipeline_data, selection_criteria="highest_score"):
    reddit_posts = pipeline_data.get("reddit_posts", [])
    downloaded_reddit_posts = pipeline_data.get("downloaded_reddit_posts", [])

    if not reddit_posts or not downloaded_reddit_posts:
        raise ValueError("No Reddit posts or downloaded posts found in pipeline data.")

    if selection_criteria == "highest_score":
        selected_index = max(
            range(len(reddit_posts)),
            key=lambda i: reddit_posts[i]["score"],
        )
    elif selection_criteria == "most_comments":
        selected_index = max(
            range(len(reddit_posts)),
            key=lambda i: reddit_posts[i]["comments"],
        )
    elif selection_criteria == "manual":
        print("Available Stories:")
        for i, post in enumerate(reddit_posts):
            print(
                f"{i + 1}. {post['title']} (Score: {post['score']}, Comments: {post['comments']})"
            )

        selected_index = int(input("Select a story by number: ")) - 1
        if selected_index < 0 or selected_index >= len(reddit_posts):
            raise ValueError("Invalid selection.")
    else:
        raise ValueError(
            "Invalid selection criteria. Choose 'highest_score', 'most_comments', or 'manual'."
        )

    selected_post = reddit_posts[selected_index]
    selected_post_file = downloaded_reddit_posts[selected_index]

    if not os.path.exists(selected_post_file):
        raise FileNotFoundError(f"Selected post file not found: {selected_post_file}")

    with open(selected_post_file, "r") as f:
        post_content = json.load(f)

    return {
        "title": selected_post["title"],
        "text_content": post_content.get("text_content", ""),
    }


def vocode_text_to_audio(
    text, output_path="data/scraped_data/audio", segment_length=1000, voice="onyx"
):
    if not text:
        raise ValueError("Text content is empty.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    text_segments = textwrap.wrap(text, segment_length, break_long_words=False)
    audio_files = []

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables.")

    client = openai.Client(
        api_key=api_key,
    )

    for i, segment in enumerate(text_segments):
        print(f"Processing segment {i + 1}/{len(text_segments)}...")
        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=segment,
            )

            audio_filename = os.path.join(output_path, f"segment_{i + 1}.mp3")
            response.stream_to_file(audio_filename)

            print(f"Audio saved to: {audio_filename}")
            audio_files.append(audio_filename)
        except Exception as e:
            print(f"Error processing segment {i + 1}: {e}")

    return audio_files


def generate_captions(
    audio_files,
    output_path="data/scraped_data/captions",
    caption_model="stt",
):
    if not audio_files:
        raise ValueError("No audio files provided.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    caption_files = []

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables.")

    client = openai.Client(
        api_key=api_key,
    )

    for audio_file in audio_files:
        with open(audio_file, "rb") as audio:
            print(f"Generating captions for: {audio_file}...")
            try:
                response = client.audio.transcriptions.create(
                    file=audio,
                    model="whisper-1",
                    response_format="verbose_json",
                    language="en",
                    timestamp_granularities=["word"],
                )

                output_filename = os.path.join(
                    output_path, f"{os.path.basename(audio_file)}.json"
                )
                with open(output_filename, "w") as json_file:
                    json.dump(response.to_dict(), json_file, indent=4)

                caption_files.append(output_filename)
                print(f"Captions saved to: {output_filename}")

            except Exception as e:
                print(f"Error generating captions for {audio_file}: {e}")

    return caption_files


if __name__ == "__main__":
    load_dotenv()

    pipeline_data = load_pipeline_data()

    print("Selecting a story...")
    selected_story = select_story(pipeline_data, selection_criteria="highest_score")
    print("\nSelected Story:")
    print(f"Title: {selected_story['title']}")
    print(f"Content: {selected_story['text_content']}")

    print("Vocoding text into speech...")
    audio_file_paths = vocode_text_to_audio(
        text=selected_story["text_content"],
    )

    print("\nGenerated Audio Files:")
    for audio_file in audio_file_paths:
        print(audio_file)

    print("Generating captions for audio files...")
    caption_file_paths = generate_captions(audio_file_paths)

    print("\nGenerated Caption Files:")
    for caption_file in caption_file_paths:
        print(caption_file)
