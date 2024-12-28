import os
import json
from moviepy.video.io.VideoFileClip import VideoFileClip
from concurrent.futures import ProcessPoolExecutor


def load_pipeline_data(filepath="data/scraped_data/combined_data.json"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Pipeline data file not found: {filepath}")

    with open(filepath, "r") as f:
        data = json.load(f)

    return data


def process_segment(
    video_path, start_time, end_time, target_width, target_height, output_path
):
    video = VideoFileClip(video_path).subclipped(start_time, end_time)

    segment_aspect_ratio = video.w / video.h
    target_aspect_ratio = target_width / target_height

    if segment_aspect_ratio > target_aspect_ratio:
        resized_segment = video.resized(height=target_height)
        crop_x1 = (resized_segment.w - target_width) / 2
        crop_x2 = crop_x1 + target_width
        cropped_segment = resized_segment.cropped(x1=crop_x1, x2=crop_x2)
    else:
        resized_segment = video.resized(width=target_width)
        crop_y1 = (resized_segment.h - target_height) / 2
        crop_y2 = crop_y1 + target_height
        cropped_segment = resized_segment.cropped(y1=crop_y1, y2=crop_y2)

    segment_filename = os.path.join(output_path, f"segment_{start_time}_{end_time}.mp4")
    cropped_segment.write_videofile(
        segment_filename, codec="h264_videotoolbox", audio_codec="aac"
    )
    return segment_filename


def cut_video_into_segments_parallel(
    video_path,
    segment_duration=45,
    output_path="data/scraped_data/video_segments",
    target_width=1080,
    target_height=1920,
):
    video = VideoFileClip(video_path)
    total_duration = int(video.duration)
    segment_ranges = [
        (start_time, min(start_time + segment_duration, total_duration))
        for start_time in range(0, total_duration, segment_duration)
    ]
    video.close()

    segment_paths = []
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(
                process_segment,
                video_path,
                start_time,
                end_time,
                target_width,
                target_height,
                output_path,
            )
            for start_time, end_time in segment_ranges
        ]

        for future in futures:
            segment_paths.append(future.result())

    return segment_paths


if __name__ == "__main__":
    pipeline_data = load_pipeline_data()

    downloaded_videos = pipeline_data.get("downloaded_youtube_videos", [])
    if not downloaded_videos:
        raise ValueError("No downloaded videos found in pipeline data.")

    input_video = downloaded_videos[0]
    print(f"Cutting video: {input_video}")

    video_segments = cut_video_into_segments_parallel(
        video_path=input_video,
        segment_duration=60,
    )

    print("\nGenerated Video Segments:")
    for segment in video_segments:
        print(segment)
